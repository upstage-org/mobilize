<script lang="ts" setup>
import { ref, watch, watchEffect, inject, computed } from "vue";
import { useQuery } from "@vue/apollo-composable";
import { useDebounceFn } from "@vueuse/core";
import gql from "graphql-tag";
import { StudioGraph } from "models/studio";
import { inquiryVar } from "apollo";
import moment, { Moment } from "moment";
import configs from "config";
import Navbar from "../Navbar.vue";

const to = (path: string) => `${configs.UPSTAGE_URL}/${path}`;
const { result, loading } = useQuery<StudioGraph>(gql`
  query StageFilter {
    whoami {
      username
      displayName
      roleName
    }
    users(active: true) {
      id
      username
      displayName
    }
    stages(input:{}) {
      edges {
        id
        name
        createdOn
        owner {
          username
          displayName
        }
      }
    }
    tags {
      id
      name
      color
      createdOn
    }
    mediaTypes {
      id
      name
    }
  }
`);

const name = ref("");
const owners = ref([]);
const types = ref([]);
const stages = ref([]);
const tags = ref([]);
const dates = ref<[Moment, Moment] | undefined>();

const ranges = {
  Today: [moment().startOf("day"), moment().endOf("day")],
  Yesterday: [
    moment().subtract(1, "day").startOf("day"),
    moment().subtract(1, "day").endOf("day"),
  ],
  "Last 7 days": [moment().subtract(7, "days"), moment()],
  "This month": [moment().startOf("month"), moment().endOf("day")],
  "Last month": [
    moment().subtract(1, "month").startOf("month"),
    moment().subtract(1, "month").endOf("month"),
  ],
  "This year": [moment().startOf("year"), moment().endOf("day")],
};

const updateInquiry = (vars: any) =>
  inquiryVar({
    ...inquiryVar(),
    ...vars,
  });

const watchInquiryVar = (vars: any) => {
  types.value = vars.mediaTypes ?? [];
  tags.value = vars.tags ?? [];
  inquiryVar.onNextChange(watchInquiryVar);
};
inquiryVar.onNextChange(watchInquiryVar);

watchEffect(() => {
  updateInquiry({
    owners: owners.value,
    stages: stages.value,
    tags: tags.value,
    mediaTypes: types.value,
  });
});
watch(
  name,
  useDebounceFn(() => {
    updateInquiry({ name: name.value });
  }, 500),
);
watch(dates, (dates) => {
  updateInquiry({
    createdBetween: dates
      ? [
          dates[0].startOf("day").format("YYYY-MM-DD"),
          dates[1].endOf("day").format("YYYY-MM-DD"),
        ]
      : undefined,
  });
});
const clearFilters = () => {
  name.value = "";
  owners.value = [];
  types.value = [];
  stages.value = [];
  tags.value = [];
  dates.value = undefined;
};
const hasFilter = computed(
  () =>
    name.value ||
    owners.value.length ||
    types.value.length ||
    stages.value.length ||
    tags.value.length ||
    dates.value,
);
const handleFilterOwnerName = (keyword: string, option: any) => {
  const s = keyword.toLowerCase();
  return (
    option.value.toLowerCase().includes(s) ||
    option.label.toLowerCase().includes(s)
  );
};

const VNodes = (_: any, { attrs }: { attrs: any }) => {
  return attrs.vnodes;
};
</script>

<template>
  <a-affix :offset-top="0">
    <a-space class="shadow rounded-xl px-4 py-2 bg-white flex justify-between">
      <a-space class="flex-wrap">
        <RouterLink to="/stages/new-stage">
          <a-button type="primary">
            <PlusOutlined /> {{ $t("new") }} {{ $t("stage") }}
          </a-button>
        </RouterLink>
        <a-input-search
          allowClear
          class="w-48"
          placeholder="Search stage"
          v-model:value="name"
        />
        <a-select
          allowClear
          showArrow
          :filterOption="handleFilterOwnerName"
          mode="tags"
          style="min-width: 124px"
          placeholder="Owners"
          :loading="loading"
          v-model:value="owners"
          :options="
            result
              ? result.users.map((e) => ({
                  value: e.username,
                  label: e.displayName || e.username,
                }))
              : []
          "
        >
          <template #dropdownRender="{ menuNode: menu }">
            <v-nodes :vnodes="menu" />
            <a-divider style="margin: 4px 0" />
            <div
              class="w-full cursor-pointer text-center"
              @mousedown.prevent
              @click.stop.prevent="owners = []"
            >
              <team-outlined />&nbsp;All players
            </div>
          </template>
        </a-select>
        <a-range-picker
          :placeholder="['Created from', 'to date']"
          v-model:value="dates as any"
          :ranges="ranges as any"
        />
        <a-button v-if="hasFilter" type="dashed" @click="clearFilters">
          <ClearOutlined />Clear Filters
        </a-button>
      </a-space>
      <Navbar />
    </a-space>
  </a-affix>
</template>
