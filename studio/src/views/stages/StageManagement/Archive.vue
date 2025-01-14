<template>
  <div class="has-text-right is-fullwidth pb-3">
    <button class="button ml-2 is-light" @click="downloadChatLog('public')">
      <span>{{ $t("download_all_audience_chat") }}</span>
    </button>
    <button class="button ml-2 is-light" @click="downloadChatLog('player')">
      <span>{{ $t("download_all_player_chat") }}</span>
    </button>
    <ClearChat />
    <SweepStage :archive="true">{{ $t("archive_performance") }}</SweepStage>
  </div>

  <DataTable :data="sessions" :headers="headers">
    <template #name="{ item }">
      <div v-if="item.name">
        <b>{{ item.name }}</b>
      </div>
      <small v-if="item.description" class="has-text-dark">{{
        item.description
      }}</small>
      <small v-else class="has-text-dark">
        <span v-if="item.recording">{{ $t("recorded") }}</span>
        <span v-else>{{ $t("auto_recorded") }}</span>
        <span v-if="item.chatless"> on {{ date(item.createdOn) }}</span>
        <span v-else> from {{ date(item.begin) }} to {{ date(item.end) }}</span>
      </small>
    </template>
    <template #public-chat="{ item }">
      <Modal>
        <template #trigger>
          <button class="button is-light">
            <Icon src="chat.svg" />
          </button>
        </template>
        <template #header>
          Audience chats from {{ date(item.begin) }}
          <span v-if="item.begin !== item.end">to {{ date(item.end) }}</span>
        </template>
        <template #content>
          <Messages :messages="item.publicMessages" from="archive" />
        </template>
      </Modal>
      <button class="button is-light" @click="downloadChatLog('public', item)">
        <Icon src="download.svg" />
      </button>
    </template>
    <template #private-chat="{ item }">
      <Modal>
        <template #trigger>
          <button class="button is-light">
            <Icon src="chat.svg" />
          </button>
        </template>
        <template #header>
          Player chats from {{ date(item.begin) }}
          <span v-if="item.begin !== item.end">to {{ date(item.end) }}</span>
        </template>
        <template #content>
          <Messages :messages="item.privateMessages" from="archive" />
        </template>
      </Modal>
      <button class="button is-light" @click="downloadChatLog('private', item)">
        <Icon src="download.svg" />
      </button>
    </template>
    <template #replay="{ item }">
      <router-link :to="`/replay/${stage.fileLocation}/${item.id}`"
        :class="`button ${item.recording ? 'is-primary' : 'is-dark'}`">
        <i class="fas fa-video"></i>
      </router-link>
    </template>
    <template #actions="{ item }">
      <CustomConfirm @confirm="(complete) => updatePerformance(item, complete)" :loading="updating" :only-yes="true">
        <Field v-model="item.name" label="Performance Name" required />
        <Field label="Description">
          <textarea class="textarea" v-model="item.description" rows="3"></textarea>
        </Field>
        <template #yes>
          <span>{{ $t("save") }}</span>
        </template>
        <template #trigger>
          <button class="button is-light">
            <Icon src="edit.svg" />
          </button>
        </template>
      </CustomConfirm>
      <CustomConfirm @confirm="(complete) => deletePerformance(item, complete)" :loading="deleting">
        <template #trigger>
          <button class="button is-light is-danger">
            <Icon src="delete.svg" />
          </button>
        </template>
        <div class="has-text-centered">
          Deleting this performance will also delete
          <span class="has-text-danger">{{
            $t("all_of_its_replay_and_chat")
          }}</span>. This cannot be undone!
          <strong>Are you sure you want to continue?</strong>
        </div>
      </CustomConfirm>
    </template>
  </DataTable>
</template>

<script>
import Messages from "components/stage/Chat/Messages.vue";
import DataTable from "components/DataTable/index.vue";
import Modal from "components/Modal.vue";
import Icon from "components/Icon.vue";
import CustomConfirm from "components/CustomConfirm.vue";
import Field from "components/form/Field.vue";
import ClearChat from "./ClearChat.vue";
import SweepStage from "./SweepStage.vue";
import { computed, inject } from "vue";
import moment from "moment";
import humanizeDuration from "humanize-duration";
import { useMutation } from "services/graphql/composable";
import { stageGraph } from "services/graphql";

export default {
  components: {
    Messages,
    DataTable,
    ClearChat,
    SweepStage,
    Modal,
    Icon,
    CustomConfirm,
    Field,
  },
  setup: () => {
    const stage = inject("stage");
    const refresh = inject("refresh");

    const date = (value) => {
      return value ? moment(value).format("YYYY-MM-DD") : "Now";
    };

    const headers = [
      {
        title: "Name",
        slot: "name",
      },
      {
        title: "Audience Chat",
        slot: "public-chat",
        align: "center",
      },
      {
        title: "Player Chat",
        slot: "private-chat",
        align: "center",
      },
      {
        title: "Replay",
        slot: "replay",
      },
      {
        title: "Messages",
        render: (item) => item.messages.length,
        align: "center",
      },
      {
        title: "Length",
        render: (item) => humanizeDuration(item.duration, { round: true }),
        align: "center",
      },
      {
        title: "Archived On",
        key: "createdOn",
        type: "date",
      },
      {
        title: "",
        slot: "actions",
      },
    ];
    const sessions = computed(() => {
      const res = [];
      if (stage.value) {
        const { performances, chats } = stage.value;
        (performances || []).forEach((p) => {
          p.messages = chats
            .filter((c) => c.performanceId === p.id)
            .map((c) => JSON.parse(c.payload));
          res.push(p);
        });
      }
      res.sort((a, b) => b.id - a.id);
      res.forEach((session) => {
        const messages = session.messages.filter((m) => !m.clear);
        if (messages.length) {
          session.begin = messages[0].at;
          session.end = messages[messages.length - 1].at;
          session.duration = session.end - session.begin;
        } else {
          session.chatless = true;
          session.duration = 0;
        }
      });
      res.forEach((session) => {
        session.privateMessages = session.messages.filter(
          (m) => m.isPrivate || m.clearPlayerChat,
        );
        session.publicMessages = session.messages.filter(
          (m) => !m.isPrivate && !m.clearPlayerChat,
        );
      });
      return res;
    });

    let textFile;

    const makeTextFile = function (content) {
      const data = new Blob(content, { type: "text/plain" });

      // If we are replacing a previously generated file we need to
      // manually revoke the object URL to avoid memory leaks.
      if (textFile !== null) {
        window.URL.revokeObjectURL(textFile);
      }

      textFile = window.URL.createObjectURL(data);

      // returns a URL you can use as a href
      return textFile;
    };
    const downloadChatLog = (option, session) => {
      const link = document.createElement("a");
      let content = [];
      if (option == "public") {
        if (session) {
          link.setAttribute(
            "download",
            `${stage.value.name}-Audience-chat-${session.end
              ? timeStamp(session.end)
              : timeStamp(session.createdOn)
            }.txt`,
          );
          content = session.publicMessages.map((item) => {
            let line = "";
            if (item.clear) {
              line = "---------------- Clear Chat ----------------";
            } else {
              line = `${item.user}: ${item.message}`;
            }
            return `${line}\r\n`;
          });
        } else {
          link.setAttribute(
            "download",
            `${stage.value.name}-Audience-chat.txt`,
          );
          sessions.value.forEach((session) => {
            content = content.concat(
              session.publicMessages.map((item) => {
                if (item.clear) {
                  return `---------------- Clear Chat ----------------\r\n`;
                } else {
                  return `${item.user}: ${item.message}\r\n`;
                }
              }),
            );
          });
        }
      } else {
        if (session) {
          link.setAttribute(
            "download",
            `${stage.value.name}-Player-chat-${session.end
              ? timeStamp(session.end)
              : timeStamp(session.createdOn)
            }.txt`,
          );
          content = session.privateMessages.map((item) => {
            let line = "";
            if (item.clearPlayerChat) {
              line = "---------------- Clear Chat ----------------";
            } else {
              line = `${item.user}: ${item.message}`;
            }
            return `${line}\r\n`;
          });
        } else {
          link.setAttribute("download", `${stage.value.name}-Player-chat.txt`);
          sessions.value.forEach((session) => {
            content = content.concat(
              session.privateMessages.map((item) => {
                if (item.clearPlayerChat) {
                  return `---------------- Clear Chat ----------------\r\n`;
                } else {
                  return `${item.user}: ${item.message}\r\n`;
                }
              }),
            );
          });
        }
      }
      link.href = makeTextFile(content);
      document.body.appendChild(link);

      // wait for the link to be added to the document
      window.requestAnimationFrame(function () {
        const event = new MouseEvent("click");
        link.dispatchEvent(event);
        document.body.removeChild(link);
      });
    };

    const padTo2Digits = (num) => {
      return num.toString().padStart(2, "0");
    };

    const formatDate = (date) => {
      return (
        [padTo2Digits(date.getHours()), padTo2Digits(date.getMinutes())].join(
          "",
        ) +
        "-" +
        [
          padTo2Digits(date.getDate()),
          padTo2Digits(date.getMonth() + 1),
          date.getFullYear(),
        ].join("")
      );
    };

    const timeStamp = (value) => {
      const date = new Date(value);
      return formatDate(date);
    };

    const { loading: updating, save: updateMutation } = useMutation(
      stageGraph.updatePerformance,
    );
    const updatePerformance = async (item, complete) => {
      await updateMutation(
        "Performance updated successfully!",
        item.id,
        item.name,
        item.description,
      );
      complete();
    };

    const { loading: deleting, save: deleteMutation } = useMutation(
      stageGraph.deletePerformance,
    );
    const deletePerformance = async (item, complete) => {
      await deleteMutation("Performance deleted successfully!", item.id);
      complete();
      if (refresh) {
        refresh(stage.value.id);
      }
    };

    return {
      stage,
      sessions,
      downloadChatLog,
      headers,
      date,
      updatePerformance,
      updating,
      deletePerformance,
      deleting,
    };
  },
};
</script>

<style scoped>
.button.is-light>img {
  max-width: unset;
}
</style>
