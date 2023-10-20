import { ReportType, reportApi } from "@/api";
import { Button, Modal } from "antd";
import { FC } from "react";
import { useTplForm } from "./modals/useTplForm";

interface Props {
  row: ReportType.TemplateListData;
  onSuccess?: () => void;
}

const Component: FC<Props> = (props) => {
  const { openModal, form } = useTplForm();

  // 编辑
  function onEdit(row: ReportType.TemplateListData) {
    openModal({ isAdd: false }).then(() => {
      form.setFieldsValue(row);
    });
  }

  // 删除
  function onDelete(row: ReportType.TemplateListData) {
    Modal.confirm({
      title: "提示",
      content: "确认删除该数据吗？",
      onOk: async () => {
        await reportApi.api.apiTemplatesTidDelete(
          row.tid,
          {},
          { successTip: true }
        );
        props.onSuccess?.();
      },
    });
  }

  return (
    <>
      <Button type="link" size="small" onClick={() => onEdit(props.row)}>
        编辑
      </Button>
      <Button
        type="link"
        size="small"
        danger
        onClick={() => onDelete(props.row)}
      >
        删除
      </Button>
    </>
  );
};

export default Component;
