import { ReportType, reportApi } from "@/api";
import { FC, useContext, useEffect, useState } from "react";
import CommonTable, { ColumnsType } from "@/components/commonTable";
import { DateTime } from "@/components/datetime";
import { useCloneForm } from "./modals/useCloneForm";
import { Button } from "antd";
import { VersionContext } from ".";

interface Props {
  row: ReportType.TemplateListData;
}

const Component: FC<Props> = (props) => {
  const { targetTid, setTargetTid } = useContext(VersionContext);
  const [list, setList] = useState<ReportType.TemplateListData[]>();
  const [loading, setLoading] = useState(false);
  const { openModal } = useCloneForm();
  const { row } = props;

  useEffect(() => {
    fetchVersion(row.tid);
  }, [row.tid]);

  useEffect(() => {
    if (targetTid === row.tid) {
      fetchVersion(targetTid);
    }
  }, [targetTid, row.tid]);

  async function fetchVersion(tid: string) {
    setLoading(true);
    try {
      const rsp = await reportApi.api.apiTemplatesTidVersionsGet(tid);
      setList(rsp.data ?? []);
    } finally {
      setLoading(false);
    }
  }

  const columns: ColumnsType<ReportType.TemplateListData> = [
    {
      title: "操作",
      dataIndex: "action",
      width: 50,
      align: "center",
      render: (_, childRow) => (
        <Button
          type="link"
          size="small"
          onClick={() =>
            openModal({
              row: childRow,
              onSuccess: setTargetTid,
            })
          }
        >
          克隆
        </Button>
      ),
    },
    {
      title: "版本ID",
      width: 100,
      dataIndex: "versionId",
    },
    {
      title: "更新日期",
      ellipsis: false,
      dataIndex: "updatedAt",
      render: (value) => <DateTime value={value} />,
    },
  ];

  return (
    <CommonTable<ReportType.TemplateListData>
      loading={loading}
      dataSource={list}
      columns={columns}
      pagination={false}
      rowKey="versionId"
    ></CommonTable>
  );
};

export default Component;
