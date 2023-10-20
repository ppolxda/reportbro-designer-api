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

/**
 * ErrorResponse
 * Error Response.
 */
export interface ErrorResponse {
  /** Error code */
  code: number;
  /** Error message */
  error: string;
}

/** HTTPValidationError */
export interface HTTPValidationError {
  /** Detail */
  detail?: ValidationError[];
}

/**
 * RequestCloneTemplate
 * RequestCloneTemplate.
 */
export interface RequestCloneTemplate {
  /** Clone from template id */
  fromTid: string;
  /**
   * Clone from Template version id
   * @default ""
   */
  fromVersionId?: string;
}

/**
 * RequestCreateTemplate
 * RequestCreateTemplate.
 */
export interface RequestCreateTemplate {
  /** Template name */
  templateName: string;
  /** Template type */
  templateType: string;
}

/**
 * RequestGenerateDataTemplate
 * RequestGenerateTemplate.
 */
export interface RequestGenerateDataTemplate {
  /** Template id */
  tid: string;
  /** Template version id */
  versionId: null;
  /** Source Data */
  data?: object;
}

/**
 * RequestGenerateTemplate
 * RequestGenerateTemplate.
 */
export interface RequestGenerateTemplate {
  /**
   * Output Format(pdf|xlsx)
   * @default "pdf"
   * @pattern ^(pdf|xlsx)$
   */
  outputFormat?: string;
  /** Source Data */
  data: object;
}

/**
 * RequestGenerateUrlTemplate
 * RequestGenerateTemplate.
 */
export interface RequestGenerateUrlTemplate {
  /** Download url for pdf */
  pdfUrl: string;
}

/**
 * RequestMultiGenerateTemplate
 * RequestMultiGenerateTemplate.
 */
export interface RequestMultiGenerateTemplate {
  /**
   * Output Format(pdf|xlsx)
   * @default "pdf"
   * @pattern ^(pdf|xlsx)$
   */
  outputFormat?: string;
  /** Input templates list */
  templates?: (
    | RequestGenerateDataTemplate
    | RequestGenerateUrlTemplate
    | (RequestGenerateDataTemplate & RequestGenerateUrlTemplate)
  )[];
}

/**
 * RequestReviewTemplate
 * RequestReviewTemplate.
 */
export interface RequestReviewTemplate {
  /**
   * Output Format(pdf|xlsx)
   * @default "pdf"
   * @pattern ^(pdf|xlsx)$
   */
  outputFormat?: string;
  /** Source Data */
  data: object;
  /** Template Data */
  report: object;
  /** Is test data */
  isTestData: boolean;
}

/**
 * RequestUploadTemplate
 * RequestUploadTemplate.
 */
export interface RequestUploadTemplate {
  /** Template Data */
  report: object;
}

/**
 * TemplateDataResponse
 * TemplateDataResponse.
 */
export interface TemplateDataResponse {
  /** Error code */
  code: number;
  /** Error message */
  error: string;
  /** Data */
  data: TemplateListData;
}

/**
 * TemplateDescData
 * TemplateList.
 */
export interface TemplateDescData {
  /** Template id */
  tid: string;
  /** Template version id */
  versionId: string;
  /** Template name */
  templateName: string;
  /** Template type */
  templateType: string;
  /**
   * update at
   * @format date-time
   * @default ""
   */
  updatedAt?: string;
  /** Templage config */
  report?: object;
  /** Template Designer Page */
  templateDesignerPage: string;
}

/**
 * TemplateDescResponse
 * TemplateDescResponse.
 */
export interface TemplateDescResponse {
  /** Error code */
  code: number;
  /** Error message */
  error: string;
  /** Data */
  data: TemplateDescData;
}

/**
 * TemplateDownLoadData
 * TemplateDownLoadData.
 */
export interface TemplateDownLoadData {
  /** Pdf download key */
  downloadKey: string;
  /** Pdf download url */
  downloadUrl: string;
}

/**
 * TemplateDownLoadResponse
 * TemplateDownLoadResponse.
 */
export interface TemplateDownLoadResponse {
  /** Error code */
  code: number;
  /** Error message */
  error: string;
  /** Data */
  data: TemplateDownLoadData;
}

/**
 * TemplateListData
 * TemplateList.
 */
export interface TemplateListData {
  /** Template id */
  tid: string;
  /** Template version id */
  versionId: string;
  /** Template name */
  templateName: string;
  /** Template type */
  templateType: string;
  /**
   * update at
   * @format date-time
   * @default ""
   */
  updatedAt?: string;
  /** Template Designer Page */
  templateDesignerPage: string;
}

/**
 * TemplateListResponse
 * TemplateListResponse.
 */
export interface TemplateListResponse {
  /** Error code */
  code: number;
  /** Error message */
  error: string;
  /** Data */
  data: TemplateListData[];
}

/** ValidationError */
export interface ValidationError {
  /** Location */
  loc: any[];
  /** Message */
  msg: string;
  /** Error Type */
  type: string;
}

import axios, { AxiosInstance, AxiosRequestConfig, ResponseType } from "axios";
import qs from "qs";

export type QueryParamsType = Record<string | number, any>;

export interface FullRequestParams extends Omit<AxiosRequestConfig, "data" | "params" | "url" | "responseType"> {
  /** set parameter to `true` for call `securityWorker` for this request */
  secure?: boolean;
  /** request path */
  path: string;
  /** content type of request body */
  type?: ContentType;
  /** query params */
  query?: QueryParamsType;
  /** format of response (i.e. response.json() -> format: "json") */
  format?: ResponseType;
  /** request body */
  body?: unknown;
}

export type RequestParams = Omit<FullRequestParams, "body" | "method" | "query" | "path">;

export interface ApiConfig<SecurityDataType = unknown> extends Omit<AxiosRequestConfig, "data" | "cancelToken"> {
  securityWorker?: (
    securityData: SecurityDataType | null,
  ) => Promise<AxiosRequestConfig | void> | AxiosRequestConfig | void;
  secure?: boolean;
  format?: ResponseType;
}

export enum ContentType {
  Json = "application/json",
  FormData = "multipart/form-data",
  UrlEncoded = "application/x-www-form-urlencoded",
}

export class HttpClient<SecurityDataType = unknown> {
  public instance: AxiosInstance;
  private securityData: SecurityDataType | null = null;
  private securityWorker?: ApiConfig<SecurityDataType>["securityWorker"];
  private secure?: boolean;
  private format?: ResponseType;

  constructor({ securityWorker, secure, format, ...axiosConfig }: ApiConfig<SecurityDataType> = {}) {
    this.instance = axios.create({ ...axiosConfig, baseURL: axiosConfig.baseURL || "" });
    this.secure = secure;
    this.format = format;
    this.securityWorker = securityWorker;
  }

  public setSecurityData = (data: SecurityDataType | null) => {
    this.securityData = data;
  };

  private mergeRequestParams(params1: AxiosRequestConfig, params2?: AxiosRequestConfig): AxiosRequestConfig {
    return {
      ...this.instance.defaults,
      ...params1,
      ...(params2 || {}),
      headers: {
        ...((this.instance.defaults.headers || {}) as any),
        ...(params1.headers || {}),
        ...((params2 && params2.headers) || {}),
      },
    };
  }

  private createFormData(input: Record<string, unknown>): FormData {
    return Object.keys(input || {}).reduce((formData, key) => {
      const property = input[key];
      formData.append(
        key,
        property instanceof Blob
          ? property
          : typeof property === "object" && property !== null
          ? JSON.stringify(property)
          : `${property}`,
      );
      return formData;
    }, new FormData());
  }

  public request = async <T = any, _E = any>({
    secure,
    path,
    type,
    query,
    format,
    body,
    ...params
  }: FullRequestParams): Promise<T> => {
    const secureParams =
      ((typeof secure === "boolean" ? secure : this.secure) &&
        this.securityWorker &&
        (await this.securityWorker(this.securityData))) ||
      {};
    const requestParams = this.mergeRequestParams(params, secureParams);
    const responseFormat = format || this.format || void 0;

    if (type === ContentType.FormData && body && body !== null && typeof body === "object" && requestParams.headers) {
      requestParams.headers.common = { Accept: "*/*" };
      requestParams.headers.post = {};
      requestParams.headers.put = {};

      body = this.createFormData(body as Record<string, unknown>);
    }

    if (type === ContentType.UrlEncoded && body && body !== null) {
      body = qs.stringify(body);
    }

    return this.instance
      .request({
        ...requestParams,
        headers: {
          ...(type && type !== ContentType.FormData ? { "Content-Type": type } : {}),
          ...(requestParams.headers || {}),
        },
        params: query,
        responseType: responseFormat,
        data: body,
        url: path,
      })
      .then((response) => response.data);
  };
}

/**
 * @title Reportbro designer server
 * @version 0.0.1
 * @baseUrl /
 *
 * Reportbro designer server
 */
export class Api<SecurityDataType extends unknown> extends HttpClient<SecurityDataType> {
  api = {
    /**
     * @description Get templates List.
     *
     * @tags ReportBro Api
     * @name ApiTemplatesListGet
     * @summary Get Templates List
     * @request GET:/api/templates/list
     */
    apiTemplatesListGet: (params: RequestParams = {}) =>
      this.request<TemplateListResponse, any>({
        path: `/api/templates/list`,
        method: "GET",
        format: "json",
        ...params,
      }),

    /**
     * @description Get templates List.
     *
     * @tags ReportBro Api
     * @name ApiTemplatesTidVersionsGet
     * @summary Get Templates Versions
     * @request GET:/api/templates/{tid}/versions
     */
    apiTemplatesTidVersionsGet: (tid: string, params: RequestParams = {}) =>
      this.request<TemplateListResponse, HTTPValidationError>({
        path: `/api/templates/${tid}/versions`,
        method: "GET",
        format: "json",
        ...params,
      }),

    /**
     * @description Get templates List.
     *
     * @tags ReportBro Api
     * @name ApiTemplatesTidDescGet
     * @summary Get Templates Data
     * @request GET:/api/templates/{tid}/desc
     */
    apiTemplatesTidDescGet: (
      tid: string,
      query?: {
        /** Template version id */
        versionId?: null;
      },
      params: RequestParams = {},
    ) =>
      this.request<TemplateDescResponse, HTTPValidationError>({
        path: `/api/templates/${tid}/desc`,
        method: "GET",
        query: query,
        format: "json",
        ...params,
      }),

    /**
     * @description Templates Manage page.
     *
     * @tags ReportBro Api
     * @name ApiTemplatesPut
     * @summary Create Templates
     * @request PUT:/api/templates
     */
    apiTemplatesPut: (data: RequestCreateTemplate, params: RequestParams = {}) =>
      this.request<TemplateDataResponse, HTTPValidationError>({
        path: `/api/templates`,
        method: "PUT",
        body: data,
        type: ContentType.Json,
        format: "json",
        ...params,
      }),

    /**
     * @description Templates Manage page.
     *
     * @tags ReportBro Api
     * @name ApiTemplatesTidPut
     * @summary Create Templates, Use Own Tid
     * @request PUT:/api/templates/{tid}
     */
    apiTemplatesTidPut: (tid: string, data: RequestCreateTemplate, params: RequestParams = {}) =>
      this.request<TemplateDataResponse, HTTPValidationError>({
        path: `/api/templates/${tid}`,
        method: "PUT",
        body: data,
        type: ContentType.Json,
        format: "json",
        ...params,
      }),

    /**
     * @description Save Templates.
     *
     * @tags ReportBro Api
     * @name ApiTemplatesTidPost
     * @summary Save Templates
     * @request POST:/api/templates/{tid}
     */
    apiTemplatesTidPost: (tid: string, data: RequestUploadTemplate, params: RequestParams = {}) =>
      this.request<TemplateDataResponse, HTTPValidationError>({
        path: `/api/templates/${tid}`,
        method: "POST",
        body: data,
        type: ContentType.Json,
        format: "json",
        ...params,
      }),

    /**
     * @description Delete Templates.
     *
     * @tags ReportBro Api
     * @name ApiTemplatesTidDelete
     * @summary Delete Templates
     * @request DELETE:/api/templates/{tid}
     */
    apiTemplatesTidDelete: (
      tid: string,
      query?: {
        /** Template version id */
        versionId?: null;
      },
      params: RequestParams = {},
    ) =>
      this.request<ErrorResponse, HTTPValidationError>({
        path: `/api/templates/${tid}`,
        method: "DELETE",
        query: query,
        format: "json",
        ...params,
      }),

    /**
     * @description Clone Templates.
     *
     * @tags ReportBro Api
     * @name ApiTemplatesTidClonePost
     * @summary Clone Templates
     * @request POST:/api/templates/{tid}/clone
     */
    apiTemplatesTidClonePost: (tid: string, data: RequestCloneTemplate, params: RequestParams = {}) =>
      this.request<TemplateDataResponse, HTTPValidationError>({
        path: `/api/templates/${tid}/clone`,
        method: "POST",
        body: data,
        type: ContentType.Json,
        format: "json",
        ...params,
      }),

    /**
     * @description Review Templates Generate.
     *
     * @tags ReportBro Generate Api
     * @name ApiTemplatesReviewGeneratePut
     * @summary Generate Preview File From Template
     * @request PUT:/api/templates/review/generate
     */
    apiTemplatesReviewGeneratePut: (
      data: RequestReviewTemplate,
      query?: {
        /**
         * Disable fill empty fields for input data
         * @default false
         */
        disabled_fill?: boolean;
      },
      params: RequestParams = {},
    ) =>
      this.request<any, HTTPValidationError>({
        path: `/api/templates/review/generate`,
        method: "PUT",
        query: query,
        body: data,
        type: ContentType.Json,
        format: "json",
        ...params,
      }),

    /**
     * @description Review Templates.
     *
     * @tags ReportBro Generate Api
     * @name ApiTemplatesReviewGenerateGet
     * @summary Get Generate Preview File
     * @request GET:/api/templates/review/generate
     */
    apiTemplatesReviewGenerateGet: (
      query: {
        /**
         * Output Format(pdf|xlsx)
         * @default "pdf"
         * @pattern ^(pdf|xlsx)$
         */
        output_format?: string;
        /**
         * File Key
         * @minLength 16
         */
        key: string;
      },
      params: RequestParams = {},
    ) =>
      this.request<any, HTTPValidationError>({
        path: `/api/templates/review/generate`,
        method: "GET",
        query: query,
        format: "json",
        ...params,
      }),

    /**
     * @description Review Templates Generate.
     *
     * @tags ReportBro Generate Api
     * @name ApiTemplatesMultiGeneratePut
     * @summary Generate File From Multiple Template(Pdf Only)
     * @request PUT:/api/templates/multi/generate
     */
    apiTemplatesMultiGeneratePut: (
      data: RequestMultiGenerateTemplate,
      query?: {
        /**
         * Disable fill empty fields for input data
         * @default false
         */
        disabled_fill?: boolean;
      },
      params: RequestParams = {},
    ) =>
      this.request<TemplateDownLoadResponse, HTTPValidationError>({
        path: `/api/templates/multi/generate`,
        method: "PUT",
        query: query,
        body: data,
        type: ContentType.Json,
        format: "json",
        ...params,
      }),

    /**
     * @description Review Templates.
     *
     * @tags ReportBro Generate Api
     * @name ApiTemplatesMultiGenerateGet
     * @summary Get Generate File From Multiple Template
     * @request GET:/api/templates/multi/generate
     */
    apiTemplatesMultiGenerateGet: (
      query: {
        /**
         * File Key
         * @minLength 16
         */
        key: string;
      },
      params: RequestParams = {},
    ) =>
      this.request<any, HTTPValidationError>({
        path: `/api/templates/multi/generate`,
        method: "GET",
        query: query,
        format: "json",
        ...params,
      }),

    /**
     * @description Review Templates Generate.
     *
     * @tags ReportBro Generate Api
     * @name ApiTemplatesTidGeneratePut
     * @summary Generate File From Template
     * @request PUT:/api/templates/{tid}/generate
     */
    apiTemplatesTidGeneratePut: (
      tid: string,
      data: RequestGenerateTemplate,
      query?: {
        /** Template version id */
        versionId?: null;
        /**
         * Disable fill empty fields for input data
         * @default false
         */
        disabled_fill?: boolean;
      },
      params: RequestParams = {},
    ) =>
      this.request<TemplateDownLoadResponse, HTTPValidationError>({
        path: `/api/templates/${tid}/generate`,
        method: "PUT",
        query: query,
        body: data,
        type: ContentType.Json,
        format: "json",
        ...params,
      }),

    /**
     * @description Review Templates.
     *
     * @tags ReportBro Generate Api
     * @name ApiTemplatesTidGenerateGet
     * @summary Get Generate File
     * @request GET:/api/templates/{tid}/generate
     */
    apiTemplatesTidGenerateGet: (
      tid: string,
      query: {
        /**
         * Output Format(pdf|xlsx)
         * @default "pdf"
         * @pattern ^(pdf|xlsx)$
         */
        output_format?: string;
        /**
         * File Key
         * @minLength 16
         */
        key: string;
      },
      params: RequestParams = {},
    ) =>
      this.request<any, HTTPValidationError>({
        path: `/api/templates/${tid}/generate`,
        method: "GET",
        query: query,
        format: "json",
        ...params,
      }),
  };
  view = {
    /**
     * @description Web main page.
     *
     * @tags Static Page
     * @name ViewGet
     * @summary Main Page
     * @request GET:/view/
     */
    viewGet: (params: RequestParams = {}) =>
      this.request<any, any>({
        path: `/view/`,
        method: "GET",
        format: "json",
        ...params,
      }),

    /**
     * @description Templates Manage page.
     *
     * @tags Static Page
     * @name ViewTemplatesGet
     * @summary Templates Manage Page
     * @request GET:/view/templates
     */
    viewTemplatesGet: (params: RequestParams = {}) =>
      this.request<any, any>({
        path: `/view/templates`,
        method: "GET",
        format: "json",
        ...params,
      }),

    /**
     * @description Templates Designer page.
     *
     * @tags Static Page
     * @name ViewDesignerTidGet
     * @summary Templates Designer Page
     * @request GET:/view/designer/{tid}
     */
    viewDesignerTidGet: (
      tid: string,
      query?: {
        /** Template version id */
        version_id?: null;
        /**
         * Show Menu Debug
         * @default true
         */
        menuShowDebug?: boolean;
        /**
         * Show Menu Sidebar
         * @default false
         */
        menuSidebar?: boolean;
        /**
         * Show Menu Language(zh_cn|de_de|en_us)
         * @default "en_us"
         * @pattern ^(zh_cn|de_de|en_us)$
         */
        locale?: string;
      },
      params: RequestParams = {},
    ) =>
      this.request<any, HTTPValidationError>({
        path: `/view/designer/${tid}`,
        method: "GET",
        query: query,
        format: "json",
        ...params,
      }),
  };
}
