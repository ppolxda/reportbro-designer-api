import { FC, useEffect, useState, createContext } from "react";
import { reportApi, ReportType } from "@/api";
import CommonTable, { ColumnsType } from "@/components/commonTable";
import { DateTime } from "@/components/datetime";
import { ToolBtnProps } from "@/components/toolBtn";
import { useTplForm } from "./modals/useTplForm";
import BtnAction from "./btnAction";
import Version from "./versions";
import { ReloadOutlined } from "@ant-design/icons";
import FormatedLink from "@/components/formatedLink";

export const VersionContext = createContext({
  targetTid: "",
  setTargetTid: (_: string) => {},
});

const Component: FC = () => {
  const [list, setList] = useState<ReportType.TemplateListData[]>();
  const [loading, setLoading] = useState(false);
  const [targetTid, setTargetTid] = useState("");
  const { openModal } = useTplForm();

  useEffect(() => {
    fetchList();
  }, []);

  // 拉取列表
  async function fetchList() {
    setLoading(true);
    try {
      const rsp = await reportApi.api.apiTemplatesListGet();
      setList(rsp.data ?? []);
    } finally {
      setLoading(false);
    }
  }

  const buttons: ToolBtnProps[] = [
    {
      text: "新增",
      onClick: () => {
        openModal({ isAdd: true, onSuccess: fetchList });
      },
    },
    {
      text: "刷新",
      type: "default",
      icon: <ReloadOutlined />,
      onClick: fetchList,
    },
  ];

  const columns: ColumnsType<ReportType.TemplateListData> = [
    {
      title: "Tid",
      width: 300,
      dataIndex: "tid",
    },
    {
      title: "模版名称",
      dataIndex: "templateName",
      width: 200,
    },
    {
      title: "模版地址",
      width: 500,
      dataIndex: "templateDesignerPage",
      render: (value: string) => (
        <FormatedLink to={value} target="_blank"></FormatedLink>
      ),
    },
    {
      title: "更新日期",
      dataIndex: "updatedAt",
      width: 250,
      render: (value) => <DateTime value={value} />,
    },
    {
      title: "操作",
      dataIndex: "action",
      align: "center",
      render: (_, row) => <BtnAction row={row} onSuccess={() => fetchList()} />,
    },
  ];

  return (
    <>
      <CommonTable<ReportType.TemplateListData>
        columns={columns}
        dataSource={list}
        loading={loading}
        pagination={false}
        buttons={buttons}
        rowKey="tid"
        scroll={{ x: "100%", y: "calc(100vh - 200px)" }}
        expandable={{
          expandedRowRender: (row) => (
            <VersionContext.Provider value={{ targetTid, setTargetTid }}>
              <Version row={row} />
            </VersionContext.Provider>
          ),
        }}
      ></CommonTable>
    </>
  );
};

export default Component;
