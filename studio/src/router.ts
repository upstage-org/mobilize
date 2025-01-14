// @ts-nocheck
import { createRouter, createWebHistory } from "vue-router";
import StagesManagement from "views/stages/index.vue";
import MediaManagement from "views/media/index.vue";
import AdminSection from "views/admin/index.vue";
import PlayerManagement from "views/admin/player-management/index.vue";
import EmailNotifications from "views/admin/email-notifications/index.vue";
import Configuration from "views/admin/configuration/index.vue";
import Home from "views/Home.vue";
import store from "store";

export const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/",
      component: () => import("layout/UnAuthorized.vue"),
      children: [
        {
          path: "/",
          name: "Home",
          component: Home,
        },
        {
          path: "/login",
          name: "Login",
          component: () => import("views/Login.vue"),
        },
        {
          path: "/register",
          name: "Register",
          component: () => import("views/Register.vue"),
        },
      ],
    },
    {
      path: "/replay/:url/:id",
      name: "Replay Recording",
      component: () => import("views/replay/Layout.vue"),
    },
    {
      path: "/playground",
      name: "Playground",
      component: () => import("views/Playground.vue"),
    },
    {
      path: "/:url", // Keep it in the last of the route list so it won't block these other pages when conflict happens
      name: "Live",
      component: () => import("views/live/Layout.vue"),
    },
    {
      path: "/",
      component: () => import("layout/Authorized.vue"),
      meta: { requireAuth: true },
      name: "Dashboard",
      children: [
        {
          path: "/stages",
          meta: {
            background: "#C7DCA7",
          },
          children: [
            { path: "", component: StagesManagement, name: "Stages" },
            {
              path: "new-stage",
              component: () =>
                import("views/stages/StageManagement/index.vue"),
              name: "New Stage",
              children: [
                {
                  name: "General Stage",
                  path: "", component: () =>
                    import("views/stages/StageManagement/General.vue")
                }
              ],
            },
            {
              path: "stage-management/:id",
              component: () =>
                import("views/stages/StageManagement/index.vue"),
              props: (route) => ({ id: route.params.id }),
              children: [
                {
                  path: "",
                  name: "Stage Management",
                  component: () =>
                    import("views/stages/StageManagement/General.vue"),
                },
                {
                  name: "Stage Customisation",
                  path: "customisation",
                  component: () =>
                    import("views/stages/StageManagement/Customisation.vue"),
                },
                {
                  name: "Stage Media",
                  path: "media",
                  component: () =>
                    import("views/stages/StageManagement/Media.vue"),
                },
                {
                  name: "Archive",
                  path: "archive",
                  component: () =>
                    import("views/stages/StageManagement/Archive.vue"),
                },
              ],
            },
          ],
        },
        {
          path: "/media",
          component: MediaManagement,
          name: "Media",
          meta: {
            background: "#FFEBD8",
          },
        },
        {
          path: "/admin",
          component: AdminSection,
          name: "Admin",
          meta: {
            background: "#E6F2FF",
          },
          children: [
            { path: "player", component: PlayerManagement },
            { path: "configuration/:section?", component: Configuration },
            { path: "email-notification", component: EmailNotifications },
          ],
        }
      ],
    },
  ],
});

router.beforeEach(async (to, from, next) => {
  document.body.classList.add("waiting");
  const loggedIn = store.getters["auth/loggedIn"];

  if (to.matched.some((record) => record.meta.requireAuth) && !loggedIn) {
    next("/login");
  }

  if ((to.name === "Login" || to.name === "Register") && loggedIn) {
    next("/stages");
  }

  if (to.name === "Live") {
    document.querySelector("meta[name=viewport]").setAttribute("content", "");
  } else {
    document
      .querySelector("meta[name=viewport]")
      .setAttribute("content", "width=device-width,initial-scale=1.0");
  }

  if (to.fullPath.includes("admin") && loggedIn) {
    await store.dispatch("user/checkIsAdmin").then((isAdmin) => {
      if (!isAdmin) {
        next("/");
      }
    });
  }

  if (to.meta.requireAuth && loggedIn) {
    await store.dispatch("user/checkIsGuest").then((isGuest) => {
      if (isGuest) {
        next("/");
      }
    });
  }

  next();
  document.title = `UpStage ${to.name ? ("- " + to.name) : ""}`;
});

router.afterEach(() => {
  document.body.classList.remove("waiting");
});