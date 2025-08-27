import {useAtomValue} from "jotai";
import {setToken} from "~/auth";
import logoSvg from "./logo.svg";
import {Link, useNavigate} from "react-router";
import {useState} from "react";
import {useForm} from "react-hook-form";
import {zodResolver} from "@hookform/resolvers/zod";
import {post} from "~/net";
import {z} from "zod";

const schema = z.object({
  email: z.email('Please input correct email address'),
  password: z.string().min(8, "Password must be at least 8 characters long")
    .max(32, "Password cannot exceed 32 characters"),
});
type FormData = z.infer<typeof schema>;

export default function Login() {
  const [message, setMessage] = useState<string | null>(null);
  const [rememberMe, setRememberMe] = useState(false);
  const navigate = useNavigate();

  const { register, handleSubmit, formState: { errors, isSubmitting } } =
    useForm<FormData>({ resolver: zodResolver(schema), mode: "onBlur" });

  const onSubmit = async (data: FormData) => {
    return post("/user/login", {
      ...data, remember_me: rememberMe
    }).then(r => {
      setToken(r.data.token, rememberMe);
      navigate("/");
    }).catch(e => {
      setMessage(e.message);
    })
  };

  return (
    <>
      <div className="flex min-h-full flex-col justify-center px-6 py-12 lg:px-8">
        <div className="sm:mx-auto sm:w-full sm:max-w-sm">
          <img
            src={logoSvg}
            alt="Food Identification"
            className="mx-auto h-10 w-auto"
          />
          <h2 className="mt-10 text-center text-2xl/9 font-bold tracking-tight text-white">Sign in to your account</h2>
        </div>

        {message && <div className="mt-5 py-5 sm:mx-auto sm:w-full sm:max-w-lg text-center">
          <p className="text-red-500">{message}</p>
        </div>}

        <div className="mt-10 sm:mx-auto sm:w-full sm:max-w-sm">
          <form className="space-y-6" onSubmit={handleSubmit(onSubmit)} noValidate>
            <div>
              <label htmlFor="email" className="block text-sm/6 font-medium text-gray-100">
                Email
              </label>
              <div className="mt-2">
                <input
                  id="email" type="email"
                  {...register("email")}
                  className={`block w-full rounded-md bg-white/5 px-3 py-1.5 text-base text-white outline-1 -outline-offset-1 placeholder:text-gray-500 focus:outline-2 focus:-outline-offset-2  sm:text-sm/6
                ${errors.email ? "outline-red-500/10 focus:outline-red-500" : "outline-white/10 focus:outline-indigo-500"}`}
                />
              </div>
              {errors.email && <p className="mt-1 text-sm/6 text-red-300">{errors.email?.message}</p>}
            </div>

            <div>
              <div className="flex items-center justify-between">
                <label htmlFor="password" className="block text-sm/6 font-medium text-gray-100">Password</label>
              </div>
              <div className="mt-2">
                <input
                  id="password" type="password"
                  {...register("password")}
                  className={`block w-full rounded-md bg-white/5 px-3 py-1.5 text-base text-white outline-1 -outline-offset-1 placeholder:text-gray-500 focus:outline-2 focus:-outline-offset-2  sm:text-sm/6
                ${errors.password ? "outline-red-500/10 focus:outline-red-500" : "outline-white/10 focus:outline-indigo-500"}`}
                />
              </div>
              {errors.password && <p className="mt-1 text-sm/6 text-red-300">{errors.password?.message}</p>}
            </div>

            <div className="flex justify-between">
              <div className="flex items-center gap-2">
                <div className="group grid size-4 grid-cols-1">
                  <input
                    id="rememberMe" name="rememberMe" type="checkbox"
                    className="col-start-1 row-start-1 appearance-none rounded-sm border border-white/10 bg-white/5 checked:border-indigo-500 checked:bg-indigo-500 indeterminate:border-indigo-500 indeterminate:bg-indigo-500 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-500 disabled:border-white/5 disabled:bg-white/10 disabled:checked:bg-white/10 forced-colors:appearance-auto"
                    checked={rememberMe}
                    onChange={(e) => setRememberMe(e.target.checked)}
                  />
                  <svg fill="none" viewBox="0 0 14 14" className="pointer-events-none col-start-1 row-start-1 size-3.5 self-center justify-self-center stroke-white group-has-disabled:stroke-white/25">
                    <path d="M3 8L6 11L11 3.5" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="opacity-0 group-has-checked:opacity-100"/>
                    <path d="M3 7H11" strokeWidth={2} strokeLinecap="round" strokeLinejoin="round" className="opacity-0 group-has-indeterminate:opacity-100"/>
                  </svg>
                </div>
                <div className="text-sm/6">
                  <label htmlFor="rememberMe" className="font-medium text-white">Remember me</label>
                </div>
              </div>
              {/*<div className="text-sm">
                <a href="#" className="font-semibold text-indigo-400 hover:text-indigo-300">
                  Forgot password?
                </a>
              </div>*/}
            </div>

            <div>
              <button type="submit" className="flex w-full justify-center rounded-md bg-indigo-500 px-3 py-1.5 text-sm/6 font-semibold text-white hover:bg-indigo-400 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-500">Sign in</button>
            </div>
          </form>

          <p className="mt-10 text-center text-sm/6 text-gray-400">
            Not a member?{' '}
            <Link to="/register" className="font-semibold text-indigo-400 hover:text-indigo-300">Register now</Link>
          </p>
        </div>
      </div>
    </>
  );
}
