// @ts-nocheck
import { message } from "ant-design-vue";
import { ref } from "vue";
import { useStore } from "vuex";
const store = useStore();
export function useLoading<T extends unknown[], U>(
  operation: (...params: T) => Promise<U>,
  messages?: {
    /**
     * The loading message, which is displayed when the operation is in progress
     */
    loading: string;
    /**
     * The success message, which is displayed when the operation finished in expecting case
     * @param result The result of the operation, so that you can use it to display in your success toast content
     * @returns The string contains the message to be displayed on the toast
     */
    success: (result: U) => string;
    /**
     * The custom error message to be displayed when the operation finished in non-happy case. If let undefined, the error message from the server will be displayed.
     * @param exception The error message from the server
     * @returns The string contains the message to be displayed on the toast
     */
    error?: (exception: unknown) => string;
    /**
     * The response toast (not the loading toast) will auto dismiss after this amount of second. Pass `0` will make it permanent, leave it or pass in `undefined` will use the default value of 1.5 seconds.
     */
    seconds?: number;
  },
) {
  const key = +new Date();
  const loading = ref(false);

  return {
    loading,
    proceed: async (...params: Parameters<typeof operation>) => {
      loading.value = true;
      if (messages) {
        message.loading({ content: messages.loading, key, duration: 0 });
      }
      try {
        const result = await operation(...params);
        if (messages) {
          message.success({
            content: messages.success(result),
            key,
            duration: messages.seconds,
          });
        }
        return result;
      } catch (error) {
        if (messages) {
          message.error({
            content: messages.error ? messages.error(error) : (typeof error == "string" ? error : error.response?.errors[0].message),
            key,
            duration: messages.seconds,
          });
        }
        loading.value = false;
      } finally {
        loading.value = false;
      }
    },
  };
}

export function useUpdateUser(messages?: Parameters<typeof useLoading>[1]) {
  return useLoading((user: any, includingPassword?: any) => {
    const {
      username,
      password,
      email,
      binName,
      role,
      firstName,
      lastName,
      displayName,
      active,
      uploadLimit,
      intro,
      id,
    } = user;
    const inbound = {
      username,
      email,
      binName,
      role,
      firstName,
      lastName,
      displayName,
      active,
      uploadLimit,
      intro,
      id,
    };
    if (includingPassword) {
      inbound.password = password;
    }
    return;
  }, messages);
}
