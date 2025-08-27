import {type LoaderFunctionArgs} from "react-router";
import {atom, useAtomValue} from "jotai";
import {atomWithStorage, createJSONStorage} from "jotai/utils";

export interface User {
  u_id: string,
  email: string,
  username: string,
  avatar: string,
}

export const userAtom = atom<User | null>(null);



const TOKEN_KEY = "_token_";

let _token: string | null = null;


/**
 *
 */
export function getToken(): string | null {
  if (_token === null) {
    let token = sessionStorage.getItem(TOKEN_KEY);
    if (token === null) {
      token = localStorage.getItem(TOKEN_KEY);
    }
    _token = token;
  }
  return _token;
}

/**
 *
 */
export function haveAuth(): boolean {
  return getToken() !== null;
}

/**
 *
 * @param token
 * @param rememberMe
 */
export function setToken(token: string, rememberMe: boolean) {
  (rememberMe ? localStorage : sessionStorage).setItem(TOKEN_KEY, token);
  _token = token;
}

/**
 *
 */
export function logout() {
  _token = null;
  sessionStorage.removeItem(TOKEN_KEY);
  localStorage.removeItem(TOKEN_KEY);
}


//
// export function getTokenClient() {
//   try {
//     return sessionStorage.getItem("token");
//   } catch {
//     return null;
//   }
// }
//
export async function getUserInfo(args: LoaderFunctionArgs) {

  // console.log(token);
  // const token = getTokenClient();
  // if (!token) {
  //   const from = new URL(args.request.url).pathname + new URL(args.request.url).search;
  //   throw redirect(`/login?from=${encodeURIComponent(from)}`);
  // }
  //
  // return null;
}
