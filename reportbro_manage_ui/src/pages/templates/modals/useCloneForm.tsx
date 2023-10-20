import { ReportType, reportApi } from "@/api";
import { showCommonModal } from "@/components/commonModal";
import CommonForm from "@/components/commonForm";
import { Form, Select, FormInstance } from "antd";
import { FC, useEffect, useState } from "react";

interface CloneFormData extends ReportType.RequestCloneTemplate {
  targetTid: string;
  fromTemplateName: string;
}

const CloneForm: FC<{
  form: FormInstance<CloneFormData>;
}> = ({ form }) => {
  const [options, setOptions] = useState<ReportType.TemplateListData[]>([]);

  useEffect(() => {
    fetchOptions();
  }, []);

  // 查询选项列表
  async function fetchOptions() {
    const data = await reportApi.api
      .apiTemplatesListGet()
      ?.then((rsp) => rsp.data ?? []);

    setOptions(data);
  }

  return (
    <CommonForm
      form={form}
      labelCol={{ span: 4 }}
      formItems={[
        {
          label: "源模版",
          name: "fromTemplateName",
          inputProps: {
            disabled: true,
          },
          initialValue: form.getFieldValue("fromTemplateName"),
        },
        {
          label: "源模版版本",
          name: "fromVersionId",
          inputProps: {
            disabled: true,
          },
          initialValue: form.getFieldValue("fromVersionId"),
        },
        {
          label: "克隆到",
          name: "targetTid",
          rules: [{ required: true }],
          component: (
            <Select
              options={options.filter(
                (item) => item.tid !== form.getFieldValue("fromTid")
              )}
              showSearch
              fieldNames={{ label: "templateName", value: "tid" }}
            ></Select>
          ),
        },
      ]}
    ></CommonForm>
  );
};

export const useCloneForm = () => {
  const [form] = Form.useForm<CloneFormData>();

  // 克隆模版
  function cloneTpl() {
    return reportApi.api.apiTemplatesTidClonePost(
      form.getFieldValue("targetTid"),
      {
        fromTid: form.getFieldValue("fromTid"),
        fromVersionId: form.getFieldValue("fromVersionId"),
      },
      { successTip: true }
    );
  }

  async function openModal({
    row,
    onSuccess,
  }: {
    row: ReportType.TemplateListData;
    onSuccess?: (tid: string) => void;
  }) {
    showCommonModal({
      title: "克隆模版",
      content: <CloneForm form={form}></CloneForm>,
      onOk: async () => {
        await form.validateFields();
        await cloneTpl();
        onSuccess?.(form.getFieldValue("targetTid"));
      },
    }).then(() => {
      form.setFieldsValue({
        fromTid: row.tid,
        fromVersionId: row.versionId,
        fromTemplateName: row.templateName,
        targetTid: "",
      });
    });
  }

  return {
    openModal,
  };
};
