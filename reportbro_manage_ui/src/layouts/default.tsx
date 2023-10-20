import { FC } from "react";
import { Outlet } from "react-router-dom";
import { Layout } from "antd";
import { APP_TITLE } from "@/config";
import styled from "styled-components";

const Wrapper = styled.div`
  height: 100%;
  .header {
    color: #fff;
    font-size: 18px;
  }
  .layout {
    height: 100%;
    display: flex;
    flex-direction: column;
  }
  .layout-content {
    height: 100%;
    > section {
      height: 100%;
    }
  }
`;

const Component: FC = () => {
  return (
    <Wrapper>
      <Layout className="layout">
        <Layout.Header className="header">{APP_TITLE}</Layout.Header>
        <div className="layout-content">
          <Outlet />
        </div>
      </Layout>
    </Wrapper>
  );
};

export default Component;
