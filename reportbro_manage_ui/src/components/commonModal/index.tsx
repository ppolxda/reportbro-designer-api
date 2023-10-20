import { Modal, ModalFuncProps } from "antd";
import { Margin } from "@/styles";
import LifeCircle from "@/components/lifeCircle";

interface CommonModalProps extends ModalFuncProps {
  onMounted?: () => void;
}

export function showCommonModal(props: CommonModalProps) {
  return new Promise((resolve) => {
    const modal = Modal.confirm({
      width: 600,
      icon: null,
      title: "",
      ...props,
      content: (
        <Margin.only $top={10}>
          <LifeCircle
            onMounted={() => {
              resolve(modal);
              props?.onMounted?.();
            }}
          >
            {props.content}
          </LifeCircle>
        </Margin.only>
      ),
    });
  });
}
