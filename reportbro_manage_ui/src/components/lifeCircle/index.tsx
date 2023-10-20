import { FC, useEffect } from "react";

interface Props {
  onMounted?: () => void;
  onUnMounted?: () => void;
  children?: React.ReactNode;
}

const Component: FC<Props> = (props) => {
  const { onMounted, onUnMounted } = props;

  useEffect(() => {
    onMounted?.();
    return () => {
      onUnMounted?.();
    };
  }, [onMounted, onUnMounted]);

  return <>{props.children}</>;
};

export default Component;
