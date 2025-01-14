<script lang="ts">
import { useI18n } from "vue-i18n";
import { Button, Form, Input, Modal, Tooltip, message } from "ant-design-vue";
import { h } from "vue";
import { PropType } from "vue";
import { ref } from "vue";
import useForm from "ant-design-vue/lib/form/useForm";
import { reactive } from "vue";
import { toRaw } from "vue";
import { KeyOutlined } from "@ant-design/icons-vue";

export default {
  props: {
    player: {
      type: Object,
      required: true,
    },
    onSave: {
      type: Function as PropType<(player: any) => Promise<void>>,
    },
    saving: {
      type: Object as PropType<{ value: boolean }>,
      default: false,
    },
  },
  setup(props) {
    const { t } = useI18n();

    const visible = ref(false);

    const values = reactive({
      password: "changeitlater",
    });
    const { validate } = useForm(values, {
      password: [
        {
          required: true,
          message: t("password_required"),
        },
      ],
    });

    return () =>
      h(
        Tooltip,
        {
          title: t("change_password"),
        },
        () => [
          h(
            Button,
            {
              onClick: () => (visible.value = true),
            },
            {
              icon: () => h(KeyOutlined),
            },
          ),
          h(
            Modal,
            {
              title: t("change_password"),
              visible: visible.value,
              onCancel: () => (visible.value = false),
              onOk: async () => {
                try {
                  await validate();
                  await props.onSave?.({
                    ...props.player,
                    ...toRaw(values),
                  });
                  visible.value = false;
                } catch (error) {
                  message.error("Password is required");
                }
              },
              okButtonProps: {
                loading: props.saving.value,
              },
            },
            () => [
              h(
                Form,
                {
                  layout: "horizontal",
                  labelCol: { span: 6 },
                  wrapperCol: { span: 18 },
                },
                [
                  h(
                    Form.Item,
                    {
                      label: t("password"),
                    },
                    [
                      h(Input, {
                        value: values.password,
                        "onUpdate:value": (value: string) =>
                          (values.password = value),
                      }),
                    ],
                  ),
                ],
              ),
            ],
          ),
        ],
      );
  },
};
</script>
