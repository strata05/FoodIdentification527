import axios, {type AxiosRequestConfig, type CreateAxiosDefaults} from 'axios';
import {getToken} from "~/auth";

/**
 *
 * @param options
 */
export function createAxios(options: CreateAxiosDefaults) {
  const instance = axios.create(options);

  instance.interceptors.response.use(
    /**
     *
     * @param response
     */
    (response) => {
      const data = response.data;
      if (data && data.success) {
        return response;
      } else {
        return Promise.reject(data ? {
          code: data.error_code,
          message: data.error,
          data: data
        } : {
          code: '10000',
          message: 'data empty',
        })
      }
    },

    /**
     *
     * @param error
     */
    (error) => {
      return Promise.reject(error);
    });

  // inject token
  instance.interceptors.request.use(config => {
    const token = getToken();
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  }, error => {
    return Promise.reject(error);
  });

  return instance;
}



/**
 *
 * @param params
 * @param options
 */
function fillParams (params: any, options?: AxiosRequestConfig) {
  if (params) {
    if (!options) {
      options = {}
    }
    options.params = params;
  }
  return options;
}


/**
 *
 */
const instance = createAxios({
  baseURL: '/api/'
});

/**
 *
 * @param url
 * @param data
 * @param options
 */
export function post (url: string, data: any, options?: AxiosRequestConfig) {
  instance.defaults.headers
  return instance.post(url, data, options);
}

/**
 *
 * @param url
 * @param params
 * @param options
 */
export function get (url: string, params?: any, options?: AxiosRequestConfig) {
  return instance.get(url, fillParams(params, options));
}

