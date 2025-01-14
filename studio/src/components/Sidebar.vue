<script lang="ts">
import { LayoutSider, Menu, MenuItem, Spin, SubMenu } from "ant-design-vue";
import { useRouter } from "vue-router";
import PlayerForm from "views/admin/player-management/PlayerForm.vue";
import { h, computed } from "vue";
import {
  PictureOutlined,
  CommentOutlined,
  ReadOutlined,
  UserOutlined,
  SettingOutlined,
} from "@ant-design/icons-vue";
import configs from "config";
import { useLoading } from "hooks/mutations";
import { userGraph } from "services/graphql";
import { useStore } from "vuex";

export default {
  setup(_, { slots }) {
    const router = useRouter();

    const store = useStore();
    const whoami = computed(() => store.getters["user/whoami"]);
    const saving = computed(() => store.getters["user/loading"]);
    const system = computed(() => store.getters["config/system"]);

    const isAdmin = computed(
      () =>
        whoami.value &&
        [String(configs.ROLES.ADMIN), String(configs.ROLES.SUPER_ADMIN)].includes(String(whoami.value.role)),
    );
    return () => h(
      LayoutSider,
      {
        theme: "light",
        collapsed: true,
        class: "select-none",
        width: 240,
      },
      () => [
        h(
          Menu,
          {
            selectedKeys: [router.currentRoute.value.path],
            onSelect: (e) => e.key && router.push(e.key.toString()),
            mode: "inline",
            class: "upstage-menu",
          },
          () =>
            [
              { key: "/media", icon: PictureOutlined, label: "Media" },
              { key: "/stages", icon: CommentOutlined, label: "Stages" },
              {
                children: whoami.value
                  ? h(
                    PlayerForm,
                    {
                      player: whoami.value,
                      saving: saving.value,
                      onSave: userGraph.updateUser as any,
                      noUploadLimit: true,
                      noStatusToggle: true,
                    },
                    {
                      default: ({ onClick }: { onClick: () => void }) =>
                        h(
                          MenuItem,
                          {
                            onClick,
                          },
                          () => [h(UserOutlined), h("span", "Profile")],
                        ),
                    },
                  )
                  : h("span"),
              },
              ...(isAdmin.value
                ? [
                  {
                    children: h(
                      SubMenu,
                      {
                        key: "/admin",
                        style: {
                          margin: 4,
                          background:
                            router.currentRoute.value.path.startsWith(
                              "/admin",
                            )
                              ? router.currentRoute.value.meta.background
                              : undefined,
                        },
                      },
                      {
                        icon: () => h(SettingOutlined),
                        title: () => "Admin",
                        default: () => [
                          h(
                            MenuItem,
                            {
                              key: "/admin/player",
                            },
                            () => "Player Management",
                          ),
                          h(
                            MenuItem,
                            {
                              key: "/admin/email-notification",
                            },
                            () => "Email Notification",
                          ),
                          h(
                            MenuItem,
                            {
                              key: "/admin/configuration",
                            },
                            () => "Configuration",
                          ),
                        ],
                      },
                    ),
                  },
                ]
                : []),
              {
                icon: ReadOutlined,
                label: "Manual",
                disabled: !system.value.manual,
                onClick: () =>
                  open(
                    system.value.manual.value ??
                    "https://docs.upstage.live/",
                    "_blank",
                  ),
              },
            ].map((item) =>
              item.children
                ? item.children
                : h(
                  MenuItem,
                  {
                    key: item.key,
                    onClick: item.onClick,
                    disabled: item.disabled,
                    style: {
                      background:
                        item.key === router.currentRoute.value.path
                          ? router.currentRoute.value.meta.background
                          : undefined,
                    },
                  },
                  () => [h(item.icon), h("span", item.label)],
                ),
            ),
        ),
      ],
    )
  },
};
</script>

<style>
.ant-menu-submenu {
  margin: 4px;
}

.ant-menu-submenu-title {
  margin: 0 !important;
  width: 100% !important;
  padding-inline: calc(50% - 10px) !important;
}
</style>
