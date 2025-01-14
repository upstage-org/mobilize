<script lang="ts">
import { ref, watch, computed } from "vue";
import { useQuery } from "@vue/apollo-composable";
import { useDebounceFn } from "@vueuse/core";
import gql from "graphql-tag";
import { StudioGraph } from "models/studio";
import { inquiryVar } from "apollo";
import moment, { Moment } from "moment";
import { getSharedAuth } from "utils/common";
import { h } from "vue";
import { Button, InputSearch, RangePicker, Space } from "ant-design-vue";
import Header from "components/Header.vue";
import { PlusOutlined } from "@ant-design/icons-vue";
import { useI18n } from "vue-i18n";
import BatchPlayerCreation from "views/admin/batch-player-creation/index.vue";

export default {
  setup() {
    // const { result, loading } = useQuery<StudioGraph>(gql`
    //   query AdminPlayerFilter {
    //     adminPlayers {
    //       edges {
    //         id
    //         username
    //       }
    //     }
    //   }
    // `);

    const sharedAuth = getSharedAuth();

    const name = ref("");
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
      inquiryVar.onNextChange(watchInquiryVar);
    };
    inquiryVar.onNextChange(watchInquiryVar);

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
      dates.value = undefined;
    };

    const hasFilter = computed(() => name.value || dates.value);
    const { t } = useI18n();
    const drawerVisible = ref(false);

    return () => [
      h(BatchPlayerCreation, {
        visible: drawerVisible.value,
        onClose: () => {
          drawerVisible.value = false;
        },
      }),
      h(Header, {}, () => [
        h(
          Space,
          {
            class: "flex-wrap",
          },
          [
            h(
              Button,
              {
                icon: h(PlusOutlined),
                type: "primary",
                onClick: () => {
                  drawerVisible.value = true;
                },
              },
              [t("new_object", [t("player", 2)])],
            ),
            h(InputSearch, {
              allowClear: true,
              class: "w-48",
              placeholder: "Player name",
              value: name.value,
              "onUpdate:value": (value: string) => {
                name.value = value;
              },
            }),
            h(RangePicker as any, {
              placeholder: ["Created from", "to date"],
              value: dates.value,
              "onUpdate:value": (value: [Moment, Moment]) => {
                dates.value = value;
              },
              ranges,
            }),
            hasFilter.value &&
            h(
              Button,
              {
                type: "dashed",
                onClick: clearFilters,
              },
              [
                h("a-icon", {
                  type: "close-circle",
                }),
                "Clear Filters",
              ],
            ),
          ],
        ),
      ]),
    ];
  },
};
</script>
