<script lang="ts">
import { reactive, watch, provide } from "vue";
import type { Media } from "models/studio";
import { displayName, titleCase } from "utils/common";
import { ColumnType, TablePaginationConfig } from "ant-design-vue/lib/table";
import { SorterResult } from "ant-design-vue/lib/table/interface";
import { useI18n } from "vue-i18n";
import { Layout, Select, Space, Switch, Table, message } from "ant-design-vue";
import { h } from "vue";
import DDate from "components/display/DDate.vue";
import PlayerForm from "./PlayerForm.vue";
import ChangePassword from "./ChangePassword.vue";
import DeletePlayer from "./DeletePlayer.vue";
import type { DefaultOptionType } from "ant-design-vue/lib/select";
import Confirm from "components/Confirm.vue";
import { useUpdateUser } from "hooks/mutations";
import { useAsyncState } from "@vueuse/core";
import { computed, ComputedRef } from "vue";
import { useQuery } from "@vue/apollo-composable";
import gql from "graphql-tag";
import configs from "config";
import { useRouter } from "vue-router";

interface Pagination {
  current: number;
  pageSize: number;
  showQuickJumper: boolean;
  showSizeChanger: boolean;
  total: number;
}
interface SortQueryParams {
  sortByCreated?: boolean;
}

export default {
  setup() {
    const { t } = useI18n();
    const router = useRouter();
    const query: SortQueryParams = router.currentRoute.value.query;

    const tableParams = reactive({
      page: 1,
      limit: 10,
      sort: [query.sortByCreated ? "CREATED_ON_DESC" : "CREATED_ON_ASC"],
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

    const { result, loading, fetchMore, refetch } = useQuery(
      gql`
          query adminPlayersTable(
            $page: Int
            $limit: Int
          ) {
            adminPlayers(page: $page limit: $limit) {
              totalCount
              edges {
                id
                username
                email
                role
                firstName
                lastName
                displayName
                active
                createdOn
                uploadLimit
                intro
                canSendEmail
                lastLogin
                roleName
              }
            }
          }
        `,
      tableParams,
      { notifyOnNetworkStatusChange: true },
    );

    watch(params, () => {
      refetch();
    });

    const columns: ComputedRef<ColumnType<any>[]> = computed((): ColumnType<any>[] => [
      {
        title: t("role"),
        dataIndex: "role",
        key: "role",
        align: "center",
        sorter: {
          multiple: 1,
        },
        customRender(opt) {
          return h(
            Confirm,
            {
              title: `Are you sure you want to change ${displayName(
                opt.record,
              )}'s role?`,
              onConfirm: async ([value, selectedOption]: [
                number,
                DefaultOptionType,
              ]) => {
                await updateUser({
                  ...opt.record,
                  role: value,
                });
                message.success(
                  `Successfully switch ${displayName(opt.record)}'s role to ${(selectedOption as DefaultOptionType).label
                  }!`,
                );
              },
            },
            {
              default: (slotProps: {
                confirm: (payload: [number, DefaultOptionType]) => void;
              }) =>
                h(Select, {
                  options: Object.entries(configs.ROLES).map(([key, id]) => ({
                    value: String(id),
                    label: titleCase(key),
                  })),
                  value: opt.text,
                  onChange: (value, selectedOption) => {
                    slotProps.confirm([value as number, selectedOption]);
                  },
                }),
            },
          );
        },
      },
      {
        title: t("username"),
        key: "username",
        dataIndex: "username",
        sorter: {
          multiple: 2,
        },
      },
      {
        title: t("display_name"),
        dataIndex: "username",
        customRender(opt) {
          return displayName(opt.record);
        },
        key: "display_name",
      },
      {
        title: t("email"),
        key: "email",
        dataIndex: "email",
        sorter: {
          multiple: 3,
        },
      },
      {
        title: t("last_login"),
        dataIndex: "lastLogin",
        key: "last_login",
        sorter: {
          multiple: 4,
        },
        customRender(opt) {
          return opt.text
            ? h(DDate, {
              value: opt.text,
            })
            : "";
        },
      },
      {
        title: t("date_registered"),
        dataIndex: "createdOn",
        key: "created_on",
        sorter: {
          multiple: 5,
        },
        customRender(opt) {
          return h(DDate, {
            value: opt.text,
          });
        },
        defaultSortOrder: query.sortByCreated ? "descend" : "ascend",
      },
      {
        title: t("status"),
        dataIndex: "active",
        key: "active",
        align: "center",
        customRender(opt) {
          return h(Switch, {
            checked: opt.text,
            loading: savingUser.value,
            onChange: async (value) => {
              await updateUser({
                ...opt.record,
                active: !!value,
              });
              message.success(
                `Account ${displayName(opt.record)} ${value ? "activated" : "deactivated"
                } successfully!`,
              );
            },
          });
        },
      },
      {
        title: `${t("manage")} ${t("player")}`,
        align: "center",
        fixed: "right",
        key: "actions",
        customRender(opt) {
          return h(Space, () => [
            h(PlayerForm, {
              player: opt.record,
              saving: savingUser.value,
              onSave: async (player) => {
                await updateUser({
                  ...player,
                });
              },
              disabledIntroduction: true,
              noPasswordChange: true,
            }),
            h(ChangePassword, {
              player: opt.record,
              saving: savingUser,
              onSave: async (player) => {
                await updateUser(
                  {
                    ...player,
                  },
                  true,
                );
                message.success(
                  `Successfully reset ${displayName(player)}'s password!`,
                );
              },
            }),
            h(DeletePlayer, {
              player: opt.record,
              onDone: async (player) => {
                refresh();
                message.success(
                  `Successfully delete ${displayName(player)}'s account!`,
                );
              },
            }),
          ]);
        },
      },
    ]);

    const handleTableChange = (
      { current = 1, pageSize = 10 }: TablePaginationConfig,
      _: any,
      sorter: SorterResult<Media> | SorterResult<Media>[],
    ) => {
      const sort = (Array.isArray(sorter) ? sorter : [sorter])
        .sort(
          (a, b) =>
            (a.column?.sorter as any).multiple -
            (b.column?.sorter as any).multiple,
        )
        .map(({ columnKey, order }) =>
          `${columnKey}_${order === "ascend" ? "ASC" : "DESC"}`.toUpperCase(),
        );
      Object.assign(tableParams, {
        page: current,
        limit: pageSize,
        sort,
      });
    };

    const refresh = () => {
      refetch();
    };
    provide("refresh", () => {
      refetch();
    });

    const { proceed: updateUser, loading: savingUser } = useUpdateUser({
      loading: "Saving player information...",
      success: () => {
        refresh();
        return "Player information saved successfully!";
      },
    });

    return () =>
      h(
        Layout,
        {
          class: "w-full shadow rounded-xl bg-white overflow-hidden",
        },
        () => [
          h(Table, {
            class: "w-full overflow-auto",
            rowKey: "id",
            columns: columns.value,
            dataSource: result.value?.adminPlayers?.edges || [],
            loading: loading.value,
            onChange: handleTableChange,
            pagination: {
              showQuickJumper: true,
              showSizeChanger: true,
              total: result.value?.adminPlayers
                ? result.value.adminPlayers.totalCount
                : 0,
            } as Pagination,
          }),
        ],
      );
  },
};
</script>
