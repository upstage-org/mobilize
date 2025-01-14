// @ts-nocheck
import store from "store";
import { computed, reactive, ref } from "vue";
import hash from "object-hash";
import { message } from "ant-design-vue";
import { configGraph } from "services/graphql";
import { logout } from "utils/auth";

export const useRequest = (service, ...params) => {
  const loading = ref(false);
  const data = ref();
  const nodes = computed(() => {
    if (!data.value) return null;
    const value = Object.values(data.value)[0];
    return Array.isArray(value) ? value : [value];
  });
  const pushNode = (node, reverse) => {
    if (data.value) {
      const key = Object.keys(data.value)[0];
      let edges = data.value[key].edges;
      if (reverse) {
        edges.unshift({ node });
      } else {
        edges.push({ node });
      }
      data.value = { [key]: { edges } };
    }
  };
  const popNode = (selector) => {
    if (data.value) {
      const key = Object.keys(data.value)[0];
      let edges = data.value[key].edges;
      const position = edges.findIndex((edge) => selector(edge.node));
      edges.splice(position, 1);
      data.value = { [key]: { edges } };
    }
  };
  const totalCount = computed(() => {
    if (!data.value) return 0;
    const key = Object.keys(data.value)[0];
    return data.value[key].totalCount;
  });
  const cacheKeys = reactive([]);

  const fetch = async (...newParams) => {
    try {
      const payload = newParams.length ? newParams : params;
      const cacheKey = hash({ service, payload });
      const cached = store.state.cache.graphql[cacheKey];
      if (cached) {
        data.value = cached;
      } else {
        loading.value = true;
        data.value = await service(...payload);
        if (data.value) {
          store.commit("cache/SET_GRAPHQL_CACHE", {
            key: cacheKey,
            value: data.value,
          });
          cacheKeys.push(cacheKey);
        }
      }
      return data.value;
    } catch (error) {
      if (error.response.errors[0].message == "Invalid refresh token") {
        logout();
      }
      throw error.response.errors[0].message;
    } finally {
      loading.value = false;
    }
  };

  const clearCache = () => {
    cacheKeys.push(hash({ service, payload: params }));
    store.commit("cache/CLEAR_GRAPHQL_CACHES", { keys: cacheKeys });
    cacheKeys.length = 0;
  };

  const refresh = (...params) => {
    clearCache();
    return fetch(...params);
  };

  return {
    loading,
    data,
    nodes,
    totalCount,
    fetch,
    clearCache,
    refresh,
    pushNode,
    popNode,
  };
};

export const useMutation = (...params) => {
  const { refresh, ...rest } = useRequest(...params);
  const mutation = refresh;
  const prm = params[0];
  const save = async (success, ...params) => {
    try {
      const response = await mutation(...params);
      if (typeof success === "function") {
        success(response);
      } else {
        if (prm === configGraph.sendEmail) {
          message.emailSuccess(success); //notification.emailSuccess(success);
        } else {
          message.success(success);
        }
      }
      return response;
    } catch (error) {
      if (prm === configGraph.sendEmail) {
        message.error(error);// notification.emailError(error);
      } else {
        message.error(error);
      }
    }
  };

  return { mutation, save, ...rest };
};

export const useQuery = (...params) => {
  const { fetch, ...rest } = useRequest(...params);
  fetch();
  return { fetch, ...rest };
};

export const useFirst = (nodes) => {
  return computed(
    () => (nodes.value && nodes.value.length && nodes.value[0]) ?? {},
  );
};

export function useAttribute(node, attributeName, isJson) {
  return computed(() => {
    let value = node.value ? node.value[attributeName] : null;
    if (isJson && value) {
      value = JSON.parse(value);
    }
    return value;
  });
}

export function useOwners(nodes) {
  return computed(() => {
    let list = [];
    if (nodes.value) {
      nodes.value.forEach(({ owner }) => {
        if (!list.some((user) => user.username === owner.username)) {
          list.push(owner);
        }
      });
    }
    return list;
  });
}
