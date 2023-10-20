/* eslint-disable */
/* tslint:disable */
/*
 * ---------------------------------------------------------------
 * ## THIS FILE WAS GENERATED VIA SWAGGER-TYPESCRIPT-API        ##
 * ##                                                           ##
 * ## AUTHOR: acacode                                           ##
 * ## SOURCE: https://github.com/acacode/swagger-typescript-api ##
 * ---------------------------------------------------------------
 */

export const ErrorResponse = {
  code: "string",
  error: "string",
};

export const HTTPValidationError = {
  detail: "string",
};

export const RequestCloneTemplate = {
  fromTid: "string",
  fromVersionId: "string",
};

export const RequestCreateTemplate = {
  templateName: "string",
  templateType: "string",
};

export const RequestGenerateDataTemplate = {
  tid: "string",
  versionId: "string",
  data: "string",
};

export const RequestGenerateTemplate = {
  outputFormat: "string",
  data: "string",
};

export const RequestGenerateUrlTemplate = {
  pdfUrl: "string",
};

export const RequestMultiGenerateTemplate = {
  outputFormat: "string",
  templates: "string",
};

export const RequestReviewTemplate = {
  outputFormat: "string",
  data: "string",
  report: "string",
  isTestData: "boolean",
};

export const RequestUploadTemplate = {
  report: "string",
};

export const TemplateDataResponse = {
  code: "string",
  error: "string",
  data: "string",
};

export const TemplateDescData = {
  tid: "string",
  versionId: "string",
  templateName: "string",
  templateType: "string",
  updatedAt: "date-time",
  report: "string",
  templateDesignerPage: "string",
};

export const TemplateDescResponse = {
  code: "string",
  error: "string",
  data: "string",
};

export const TemplateDownLoadData = {
  downloadKey: "string",
  downloadUrl: "string",
};

export const TemplateDownLoadResponse = {
  code: "string",
  error: "string",
  data: "string",
};

export const TemplateListData = {
  tid: "string",
  versionId: "string",
  templateName: "string",
  templateType: "string",
  updatedAt: "date-time",
  templateDesignerPage: "string",
};

export const TemplateListResponse = {
  code: "string",
  error: "string",
  data: "string",
};

export const ValidationError = {
  loc: "string",
  msg: "string",
  type: "string",
};
