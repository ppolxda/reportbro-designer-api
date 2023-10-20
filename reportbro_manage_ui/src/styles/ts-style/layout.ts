import styled from "styled-components";

export const Padding = {
  all: styled.div<{ $value: number }>`
    padding: ${(props) => props.$value}px;
  `,
  symmetric: styled.div<{ $horizontal?: number; $vertical?: number }>`
    padding: ${(props) => props.$vertical ?? 0}
      ${(props) => props.$horizontal ?? 0}px;
  `,
  only: styled.div<{
    $top?: number;
    $bottom?: number;
    $left?: number;
    $right?: number;
  }>`
    padding-top: ${(props) => props.$top ?? 0}px;
    padding-bottom: ${(props) => props.$bottom ?? 0}px;
    padding-left: ${(props) => props.$left ?? 0}px;
    padding-right: ${(props) => props.$right ?? 0}px;
  `,
};

export const Margin = {
  all: styled.div<{ $value: number }>`
    margin: ${(props) => props.$value}px;
  `,
  symmetric: styled.div<{ $horizontal?: number; $vertical?: number }>`
    margin: ${(props) => props.$vertical ?? 0}
      ${(props) => props.$horizontal ?? 0}px;
  `,
  only: styled.div<{
    $top?: number;
    $bottom?: number;
    $left?: number;
    $right?: number;
  }>`
    margin-top: ${(props) => props.$top ?? 0}px;
    margin-bottom: ${(props) => props.$bottom ?? 0}px;
    margin-left: ${(props) => props.$left ?? 0}px;
    margin-right: ${(props) => props.$right ?? 0}px;
  `,
};
