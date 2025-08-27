import type {Route} from "./+types/home";
import logoSvg from "./logo.svg";

import {Disclosure, DisclosureButton, DisclosurePanel, Menu, MenuButton, MenuItem, MenuItems} from '@headlessui/react'
import {Bars3Icon, BellIcon, XMarkIcon} from '@heroicons/react/24/outline'
import {Link, NavLink, Outlet, redirect, useNavigate} from "react-router";
import {haveAuth, type User, userAtom} from "~/auth";
import {useAtom} from "jotai";
import {useEffect} from "react";
import {get} from "~/net";

export function meta({}: Route.MetaArgs) {
  return [
    {title: "Food Identification"},
    {name: "description", content: "AI-based Food Identification and Nutritional Recording System"},
  ];
}

const navigation = [
  {name: 'Dashboard', href: '#', current: true},
  {name: 'History', href: '#', current: false},
]

function classNames(...classes: string[]) {
  return classes.filter(Boolean).join(' ')
}

// export async function loader() {
//   if (!haveAuth()) {
//     redirect("/login");
//   }
// }

export async function clientLoader(_: Route.ClientLoaderArgs) {
  // console.log("XX")
    if (!haveAuth()) {
    return redirect("/login");
  }
}

export default function Index() {
  const [user, setUser] = useAtom(userAtom);
  useEffect(() => {
    let controller: AbortController | null = null;
    if (user === null) {
      controller = new AbortController();
      get("/user/info", null, {
        signal: controller.signal
      }).then(r => {
        setUser({...r.data.user});
      }).catch(e => {
        // TODO
      });
    }

    return () => {
      if (controller) {
        controller.abort()
      }
    }
  })

  console.log("user", user)


  return (
    <>
      <Disclosure
      as="nav"
      className="relative bg-gray-800/50 after:pointer-events-none after:absolute after:inset-x-0 after:bottom-0 after:h-px after:bg-white/10"
    >
      <div className="mx-auto max-w-7xl px-2 sm:px-6 lg:px-8">
        <div className="relative flex h-16 items-center justify-between">
          <div className="absolute inset-y-0 left-0 flex items-center sm:hidden">
            {/* Mobile menu button*/}
            <DisclosureButton
              className="group relative inline-flex items-center justify-center rounded-md p-2 text-gray-400 hover:bg-white/5 hover:text-white focus:outline-2 focus:-outline-offset-1 focus:outline-indigo-500">
              <span className="absolute -inset-0.5"/>
              <span className="sr-only">Open main menu</span>
              <Bars3Icon aria-hidden="true" className="block size-6 group-data-open:hidden"/>
              <XMarkIcon aria-hidden="true" className="hidden size-6 group-data-open:block"/>
            </DisclosureButton>
          </div>

          <div className="flex flex-1 items-center justify-center sm:items-stretch sm:justify-start">
            <div className="flex shrink-0 items-center">
              <img
                src={logoSvg}
                alt="Food Identification"
                className="h-8 w-auto"
              />
            </div>
            <div className="hidden sm:ml-6 sm:block">
              <div className="flex space-x-4">
                {navigation.map((item) => (
                  <a
                    key={item.name}
                    href={item.href}
                    aria-current={item.current ? 'page' : undefined}
                    className={classNames(
                      item.current ? 'bg-gray-950/50 text-white' : 'text-gray-300 hover:bg-white/5 hover:text-white',
                      'rounded-md px-3 py-2 text-sm font-medium',
                    )}
                  >
                    {item.name}
                  </a>
                ))}
              </div>
            </div>
          </div>

          {user ? (
            <div className="absolute inset-y-0 right-0 flex items-center pr-2 sm:static sm:inset-auto sm:ml-6 sm:pr-0">
              <button
                type="button"
                className="relative rounded-full p-1 text-gray-400 hover:text-white focus:outline-2 focus:outline-offset-2 focus:outline-indigo-500"
              >
                <span className="absolute -inset-1.5" />
                <span className="sr-only">View notifications</span>
                <BellIcon aria-hidden="true" className="size-6" />
              </button>

              {/* Profile dropdown */}
              <Menu as="div" className="relative ml-3">
                <MenuButton className="relative flex rounded-full focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-500">
                  <span className="absolute -inset-1.5" />
                  <span className="sr-only">Open user menu</span>

                  <img
                    alt={user.username}
                    src={user.avatar ? user.avatar : `https://api.dicebear.com/9.x/initials/svg?seed=${user.username}`}
                    className="size-8 rounded-full bg-gray-800 outline -outline-offset-1 outline-white/10"
                  />
                </MenuButton>

                <MenuItems
                  transition
                  className="absolute right-0 z-10 mt-2 w-48 origin-top-right rounded-md bg-gray-800 py-1 outline -outline-offset-1 outline-white/10 transition data-closed:scale-95 data-closed:transform data-closed:opacity-0 data-enter:duration-100 data-enter:ease-out data-leave:duration-75 data-leave:ease-in"
                >
                  <MenuItem>
                    <a href="#" className="block px-4 py-2 text-sm text-gray-300 data-focus:bg-white/5 data-focus:outline-hidden">
                      Sign out</a>
                  </MenuItem>
                </MenuItems>
              </Menu>
            </div>
          ) : (
            <div className="absolute inset-y-0 right-0 flex items-center pr-2 sm:static sm:inset-auto sm:ml-6 sm:pr-0">
              <Link to="login" className="block px-4 py-2 text-sm text-gray-300 data-focus:bg-white/5 data-focus:outline-hidden hover:text-gray-100 ">
                      Sign in</Link>
              <Link to="register" className="block rounded-md bg-white/10 px-3.5 py-2.5 text-center text-sm font-semibold text-gray-300 inset-ring inset-ring-white/5 hover:bg-white/20 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-white/75">
                Sign up
              </Link>
            </div>
          )}
          {/**/}
        </div>
      </div>

      <DisclosurePanel className="sm:hidden">
        <div className="space-y-1 px-2 pt-2 pb-3">
          {navigation.map((item) => (
            <DisclosureButton
              key={item.name}
              as="a"
              href={item.href}
              aria-current={item.current ? 'page' : undefined}
              className={classNames(
                item.current ? 'bg-gray-950/50 text-white' : 'text-gray-300 hover:bg-white/5 hover:text-white',
                'block rounded-md px-3 py-2 text-base font-medium',
              )}
            >
              {item.name}
            </DisclosureButton>
          ))}
        </div>
      </DisclosurePanel>
    </Disclosure>
      <Outlet />
    </>
  );
}
