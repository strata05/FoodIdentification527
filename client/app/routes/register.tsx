import logoSvg from "./logo.svg";
import {useForm} from "react-hook-form";
import {z} from "zod";
import {zodResolver} from "@hookform/resolvers/zod";
import {post} from "~/net";
import {useState} from "react";
import {Link} from "react-router";

const schema = z.object({
  email: z.email('Please input correct email address'),
  password: z.string().min(8, "Password must be at least 8 characters long")
    .max(32, "Password cannot exceed 32 characters"),
  username: z.string().min(2, "Username must be at least 2 characters long")
    .max(32, "Username cannot exceed 32 characters")
});
type FormData = z.infer<typeof schema>;



export default function Register() {
  const [regSuc, setRegSuc] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const { register, handleSubmit, formState: { errors, isSubmitting } } =
    useForm<FormData>({ resolver: zodResolver(schema), mode: "onBlur" });

  const onSubmit = async (data: FormData) => {
    return post("/user/register", data).then(r => {
      setRegSuc(true)
    }).catch(e => {
      setMessage(e.message);
    })
  };

  if (regSuc) {
    return (
      <div className="mx-auto mt-24 sm:mx-auto sm:w-ful sm:max-w-4xl 2xl:mt-20 text-center">
        <h1 className="mt-2 tracking-tight sm:text-5xl text-pretty">Account created successfully</h1>
        <p className="mt-6 text-base/7 text-gray-600 dark:text-gray-400">
          <Link to="/login" className="text-blue-500 hover:text-blue-600">Sign in</Link> to start using the app.</p>
      </div>
    )
  }

  return (
    <>
      <div className="flex min-h-full flex-col justify-center px-6 py-12 lg:px-8">
        <div className="sm:mx-auto sm:w-full sm:max-w-lg border-b border-white/10 pb-5 px-2">
          <img
            src={logoSvg}
            alt="Food Identification"
            className="h-10 w-auto"
          />
          <h2 className="mt-5 text-2xl/9 font-bold tracking-tight text-white">Create your free account</h2>
        </div>

        {message && <div className="mt-5 py-5 sm:mx-auto sm:w-full sm:max-w-lg">
          <p className="text-red-500">{message}</p>
        </div>}

        <form onSubmit={handleSubmit(onSubmit)} noValidate>
          <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-lg flex flex-col gap-8">
            <div>
              <label htmlFor="email" className="block text-sm/6 font-medium text-white">Email</label>
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
              <label htmlFor="password" className="block text-sm/6 font-medium text-white">Password</label>
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

            <div>
              <label htmlFor="username" className="block text-sm/6 font-medium text-white">Username</label>
              <div className="mt-2">
                <input
                  id="username" type="text"
                  {...register("username")}
                  className={`block w-full rounded-md bg-white/5 px-3 py-1.5 text-base text-white outline-1 -outline-offset-1 placeholder:text-gray-500 focus:outline-2 focus:-outline-offset-2  sm:text-sm/6
                ${errors.username ? "outline-red-500/10 focus:outline-red-500" : "outline-white/10 focus:outline-indigo-500"}`}
                />
              </div>
              {errors.username && <p className="mt-1 text-sm/6 text-red-300">{errors.username?.message}</p>}
            </div>

            <div>
              <button
                type="submit"
                className="flex w-full justify-center rounded-md bg-indigo-500 px-3 py-1.5 text-sm/6 font-semibold text-white hover:bg-indigo-400 focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-indigo-500"
              >
                Create account
              </button>
            </div>
          </div>
        </form>
      </div>

    </>
  );
}
