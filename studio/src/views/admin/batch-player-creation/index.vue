<script lang="ts">
import { h, reactive } from "vue";
import { Button, Drawer, Input, Space, message } from "ant-design-vue";
import { useI18n } from "vue-i18n";
import {
  SaveOutlined,
  PlusOutlined,
  DeleteOutlined,
} from "@ant-design/icons-vue";
import { computed } from "vue";
import { useMutation } from "@vue/apollo-composable";
import gql from "graphql-tag";
import { inquiryVar } from "apollo";

export default {
  props: {
    visible: {
      type: Boolean,
      default: false,
    },
    onClose: {
      type: Function,
      default: () => {},
    },
  },
  setup(props, ctx) {
    const { t } = useI18n();
    const players = reactive<
      { username: string; email: string; password: string }[]
    >([
      {
        username: "",
        email: "",
        password: "",
      },
    ]);

    const valid = computed(() => {
      return (
        players.length &&
        players.every((player) => {
          return (
            player.username &&
            player.password &&
            player.email &&
            player.email.includes("@")
          );
        })
      );
    });

    const { mutate, loading, onDone, onError } = useMutation(gql`
      mutation BatchUserCreation($users: [BatchUserInput]!) {
        batchUserCreation(users: $users) {
          users {
            id
          }
        }
      }
    `);

    onDone(() => {
      props.onClose();
      message.success(`${players.length} players created successfully!`);
      players.splice(0, players.length, {
        username: "",
        email: "",
        password: "",
      });

      inquiryVar({
        ...inquiryVar(),
        refresh: new Date(),
      });
    });

    const watchInquiryVar = (vars: any) => {
      inquiryVar.onNextChange(watchInquiryVar);
    };
    inquiryVar.onNextChange(watchInquiryVar);

    onError((e) => {
      message.error(e.message);
    });

    return () =>
      h(
        Drawer,
        {
          title: h(Space, { class: "w-full justify-between" }, [
            h("span", "Create new player"),
            h(
              Button,
              {
                class: "ml-auto",
                icon: h(SaveOutlined),
                type: "primary",
                disabled: !valid.value,
                loading: loading.value,
                onClick: () => {
                  for (const player of players) {
                    const duplicatedPlayer = players.find(
                      (p) => p !== player && p.username === player.username,
                    );
                    if (duplicatedPlayer) {
                      message.error(`Duplicated username: ${player.username}!`);
                      return;
                    }
                    const duplicatedEmail = players.find(
                      (p) => p !== player && p.email === player.email,
                    );
                    if (duplicatedEmail) {
                      message.error(`Duplicated email: ${player.email}!`);
                      return;
                    }
                  }
                  mutate({
                    users: players.map((player) => ({
                      ...player,
                    })),
                  });
                },
              },
              t("save"),
            ),
          ]),
          visible: props.visible,
          onClose: () => {
            let confirmed = true;
            if (
              players.length &&
              players.some(
                (player) => player.username || player.password || player.email,
              )
            ) {
              confirmed = confirm(
                "Are you sure you want to discard the changes?",
              );
            }
            if (confirmed) {
              props.onClose();
            }
          },
          width: 720,
        },
        () =>
          h(Space, { class: "w-full", direction: "vertical" }, () => [
            players.map((player) =>
              h(Space, { class: "w-full" }, () => [
                h(Input, {
                  placeholder: t("username"),
                  value: player.username,
                  onChange: (e) => {
                    player.username = e.target.value!;
                  },
                }),
                h(Input, {
                  type: "email",
                  placeholder: t("email"),
                  value: player.email,
                  onChange: (e) => {
                    player.email = e.target.value!;
                  },
                  status:
                    !player.email || player.email.includes("@")
                      ? undefined
                      : "warning",
                }),
                h(Input, {
                  type: "password",
                  placeholder: t("password"),
                  value: player.password,
                  onChange: (e) => {
                    player.password = e.target.value!;
                  },
                }),
                h(
                  Button,
                  {
                    icon: h(DeleteOutlined),
                    danger: true,
                    onClick: () => {
                      players.splice(players.indexOf(player), 1);
                    },
                  },
                  t("remove"),
                ),
              ]),
            ),
            h(
              Button,
              {
                class: "w-full",
                icon: h(PlusOutlined),
                type: "dashed",
                onClick: () =>
                  players.push({
                    username: "",
                    email: "",
                    password: "",
                  }),
              },
              t("new"),
            ),
          ]),
      );
  },
};
</script>
