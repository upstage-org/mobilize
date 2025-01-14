<script lang="ts" setup>
import { useMutation, useQuery } from "@vue/apollo-composable";
import { message } from "ant-design-vue";
import gql from "graphql-tag";
import {
  computed,
  reactive,
  watch,
  provide,
  ref,
  inject,
  Ref,
  ComputedRef,
  onMounted
} from "vue";
import { editingMediaVar, inquiryVar } from "apollo";
import configs from "config";
import { permissionFragment } from "models/fragment";
import {
  Media,
  MediaAttributes,
  StudioGraph,
  UploadFile,
  User,
} from "models/studio";
import { absolutePath } from "utils/common";
import MediaPreview from "./MediaPreview.vue";
import RequestPermission from "./MediaForm/RequestPermission.vue";
import RequestAcknowledge from "./MediaForm/RequestAcknowledge.vue";
import { ColumnType, TablePaginationConfig } from "ant-design-vue/lib/table";
import { SorterResult } from "ant-design-vue/lib/table/interface";
import QuickStageAssignment from "./QuickStageAssignment.vue";
import { useI18n } from "vue-i18n";
import { useStore } from "vuex";

const store = useStore();
const whoami = computed(() => store.getters["user/whoami"]);
const isAdmin = computed(() => store.getters["user/isAdmin"]);

const { t } = useI18n();
const files = inject<Ref<UploadFile[]>>("files");

const tableParams = reactive({
  page: 1,
  limit: 10,
  cursor: undefined,
  //sort: "CREATED_ON_DESC",
});
const { result: inquiryResult } = useQuery(gql`
  {
    inquiry @client
  }
`);
const params = computed(() => ({
  ...tableParams,
  ...inquiryResult.value.inquiry,
}));
const { result, loading, fetchMore, refetch } = useQuery<
  StudioGraph,
  { page: number; limit: number; sort?: string[] }
>(
  gql`
    query MediaTable(
      $page: Int
      $limit: Int
    ) {
      media(input:{
        page: $page
        limit: $limit
      }) {
        totalCount
        edges {
          id
          name
          createdOn
          size
          description
          fileLocation
          assetType {
            name
          }
          permissions {
            ...permissionFragment
          }
          copyrightLevel
          tags
          owner {
            username
            displayName
          }
          stages {
            name
            fileLocation
            id
          }
          privilege
        }
      }
    }
    ${permissionFragment}
  `,
  tableParams,
  { notifyOnNetworkStatusChange: true },
);

const updateQuery = (previousResult: StudioGraph, { fetchMoreResult }: any) => {
  return fetchMoreResult ?? previousResult;
};

onMounted(() => {
  refetch();
});

watch(params, () => {
  refetch();
});

const columns: ComputedRef<ColumnType<Media>[]> = computed((): ColumnType<Media>[] => [
  {
    title: t("preview"),
    align: "center",
    width: 96,
    key: "preview",
  },
  {
    title: t("name"),
    dataIndex: "name",
    key: "name",
    sorter: {
      multiple: 3,
    },
  },
  {
    title: t("type"),
    dataIndex: ["assetType", "name"],
    key: "asset_type_id",
    sorter: {
      multiple: 1,
    },
  },
  {
    title: t("owner"),
    dataIndex: "owner",
    key: "owner_id",
    sorter: {
      multiple: 2,
    },
  },
  {
    title: t("copyright_level"),
    dataIndex: "copyrightLevel",
    key: "copyrightLevel",
  },
  {
    title: t("stages"),
    key: "stages",
    dataIndex: "stages",
    width: 250,
  },
  {
    title: t("tags"),
    key: "tags",
    dataIndex: "tags",
    width: 250,
  },
  {
    title: t("size"),
    dataIndex: "size",
    key: "size",
    sorter: {
      multiple: 4,
    },
  },
  {
    title: t("date"),
    dataIndex: "createdOn",
    key: "created_on",
    sorter: {
      multiple: 5,
    },
    defaultSortOrder: "descend",
  },
  {
    title: `${t("manage")} ${t("media")}`,
    align: "center",
    fixed: "right",
    key: "actions",
  },
]);

interface Pagination {
  current: number;
  pageSize: number;
  showQuickJumper: boolean;
  showSizeChanger: boolean;
  total: number;
}

interface Sorter {
  column: any;
  columnKey: string;
  field: string;
  order: "ascend" | "descend";
}

const handleTableChange = (
  { current = 1, pageSize = 10 }: TablePaginationConfig,
  _: any,
  sorter: SorterResult<Media> | SorterResult<Media>[],
) => {
  const sort = (Array.isArray(sorter) ? sorter : [sorter])
    .sort(
      (a, b) =>
        (a.column?.sorter as any).multiple - (b.column?.sorter as any).multiple,
    )
    .map(({ columnKey, order }) =>
      `${columnKey}_${order === "ascend" ? "ASC" : "DESC"}`.toUpperCase(),
    );
  Object.assign(tableParams, {
    cursor:
      current > 1
        ? window.btoa(`arrayconnection:${(current - 1) * pageSize}`)
        : undefined,
    limit: pageSize,
    sort,
  });
};
const dataSource = computed(() =>
  result.value ? result.value.media.edges : [],
);

const {
  loading: deleting,
  mutate: deleteMedia,
  onDone,
} = useMutation(gql`
  mutation deleteMedia($id: ID!) {
    deleteMedia(id: $id) {
      success
      message
    }
  }
`);
onDone((result) => {
  console.log();
  if (result.data.deleteMedia.success) {
    message.success("Media deleted successfully");
  } else {
    message.error(result.data.deleteMedia.message);
  }
  fetchMore({
    variables: tableParams,
    updateQuery,
  });
});

provide("refresh", () => {
  fetchMore({
    variables: tableParams,
    updateQuery,
  });
});

const editMedia = (media: Media) => {
  editingMediaVar(media);
};

const composingMode = inject<Ref<boolean>>("composingMode");

const addFrameToEditingMedia = (media: Media) => {
  if (files && composingMode) {
    let frames = [media.src];
    const attribute = JSON.parse(media.description || "{}") as MediaAttributes;
    if (attribute.multi) {
      frames = attribute.frames;
    }
    files.value = files.value.concat(
      frames.map<UploadFile>((frame, i) => ({
        id: files.value.length + i,
        preview: absolutePath(frame),
        url: frame,
        status: "uploaded",
        file: {
          name: frame,
        } as File,
      })),
    );
    composingMode.value = false;
  }
};

const filterTag = (tag: string) => {
  inquiryVar({
    ...inquiryVar(),
    tags: [tag],
  });
};


</script>

<template>
  <a-layout class="w-full shadow rounded-xl bg-white overflow-hidden">
    <a-table class="w-full overflow-auto" :columns="columns as ColumnType<Media>[]" :data-source="dataSource"
      rowKey="id" :loading="loading" @change="handleTableChange" :pagination="{
      showQuickJumper: true,
      showSizeChanger: true,
      total: result ? result.media.totalCount : 0,
    } as Pagination
      ">
      <template #bodyCell="{ column, record, text }">
        <template v-if="column.key === 'preview'">
          <MediaPreview v-if="record.assetType" :media="record as Media" />
        </template>
        <template v-if="column.key === 'asset_type_id'">
          <span class="capitalize">{{ text }}</span>
        </template>
        <template v-if="column.key === 'owner_id'">
          <span v-if="text.displayName">
            <b>{{ text.displayName }}</b>
            <br />
            <span class="text-gray-500">{{ text.username }}</span>
          </span>
          <span v-else>
            <span>{{ text.username }}</span>
          </span>
        </template>
        <template v-if="column.key === 'stages'">
          <a v-for="(stage, i) in text" :key="i" :href="`${configs.UPSTAGE_URL}/${stage.url}`" target="_blank">
            <a-tag color="#007011">{{ stage.name }}</a-tag>
          </a>
        </template>
        <template v-if="column.key === 'tags'">
          <a-tag v-for="(tag, i) in text" :key="i" :color="tag" @click="filterTag(tag)" class="cursor-pointer">{{ tag }}
          </a-tag>
        </template>
        <template v-if="column.key === 'size'">
          <a-tag v-if="text" :color="text < 100000 ? 'green' : text < 500000 ? 'gold' : 'red'">
            <d-size :value="text" />
          </a-tag>
          <a-tag v-else>{{ $t("no_size") }}</a-tag>
        </template>
        <template v-if="column.key === 'copyrightLevel'">
          <span class="leading-4">{{
      configs.MEDIA_COPYRIGHT_LEVELS.find(
        (l) => l.value === record.copyrightLevel,
      )?.name
    }}</span>
        </template>
        <template v-if="column.key === 'created_on'">
          <d-date :value="text" />
        </template>
        <template v-if="column.key === 'actions'">
          <a-space v-if="isAdmin || record.owner.username === whoami?.username">
            <a-button type="primary" @click="editMedia(record as Media)">
              <EditOutlined />
              Edit
            </a-button>
            <a :href="absolutePath(record.src)" :download="record.name">
              <a-button>
                <template #icon>
                  <DownloadOutlined />
                </template>
              </a-button>
            </a>
            <a-popconfirm title="Are you sure you want to delete this media?" ok-text="Yes" cancel-text="No"
              @confirm="deleteMedia(record)" placement="left" :ok-button-props="{ danger: true }" loading="deleting">
              <a-button type="dashed" danger>

                <template #icon>
                  <DeleteOutlined />
                </template>
              </a-button>
            </a-popconfirm>
          </a-space>
          <a-space v-else-if="composingMode">
            <a-button type="primary" @click="addFrameToEditingMedia(record as Media)">
              <DoubleRightOutlined />
              Append frames
            </a-button>
          </a-space>
          <template v-else>
            <a-space v-if="record.privilege === 'NONE'">
              <a-tooltip>
                <template #title>You don't have permission to access this media
                </template>
                🙅‍♀️🙅‍♂️
              </a-tooltip>
            </a-space>
            <a-space v-else-if="record.privilege === 'REQUIRE_APPROVAL'">
              <RequestPermission v-if="record.copyrightLevel === 2" :media="record as Media" />
              <RequestAcknowledge v-else :media="record as Media" />
            </a-space>
            <a-space v-else-if="record.privilege === 'PENDING_APPROVAL'" direction="vertical" class="leading-4">
              <b>✅ Request sent!</b>
              <small>Please wait for the media owner's approval</small>
            </a-space>
            <a-space v-else>
              <QuickStageAssignment :media="record as Media" />
            </a-space>
          </template>
        </template>
      </template>
    </a-table>
    <slot></slot>
  </a-layout>
</template>
state/auth
