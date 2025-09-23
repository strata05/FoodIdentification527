import {useCallback, useEffect, useMemo, useRef, useState} from "react";
import { get, post } from "~/net";
import { useAtomValue } from "jotai";
import { userAtom } from "~/auth";

import { useNavigate } from "react-router";
import { getToken } from "~/auth";
import HistoryItem, {type Item} from "~/component/history-item";

type ImgItem = {
  u_id: string;
  image_id: string;
  created_at: number;
  original_name: string;
  content_type: string;
  size: number;
  relative_path: string;
};

const formatBytes = (bytes: number) => {
  if (bytes === 0) return "0 B";
  const k = 1024;
  const sizes = ["B", "KB", "MB", "GB", "TB"] as const;
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${(bytes / Math.pow(k, i)).toFixed(1)} ${sizes[i]}`;
};

const formatDate = (ms: number) => {
  try {
    const d = new Date(ms);
    return d.toLocaleString();
  } catch {
    return String(ms);
  }
};

export default function Home() {
  const nav = useNavigate();
  useEffect(() => {
    if (!getToken()) nav("/login", { replace: true });
  }, [nav]);

  const maxFiles = 5;

  const user = useAtomValue(userAtom);
  const [list, setList] = useState<ImgItem[]>([]);
  const [sel, setSel] = useState<Record<string, boolean>>({});
  const [msg, setMsg] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);
  const [dragOver, setDragOver] = useState(false);
  const [localPreviews, setLocalPreviews] = useState<
    { url: string; name: string, file: File }[]
  >([]);
  // const [pendingFiles, setPendingFiles] = useState<File[]>([]);
  const fileInputRef = useRef<HTMLInputElement | null>(null);

  // const load = async () => {
  //   try {
  //     const r = await get("/images", { limit: 50 });
  //     setList(r.data.items);
  //   } catch (e: any) {
  //     setMsg(e?.message ?? "load images failed");
  //   }
  // };
  //
  // useEffect(() => {
  //   load();
  // }, []);

  useEffect(() => {
    return () => localPreviews.forEach((p) => URL.revokeObjectURL(p.url));
  }, [localPreviews]);

  const selectedIds = useMemo(
    () =>
      Object.entries(sel)
        .filter(([, v]) => v)
        .map(([k]) => k),
    [sel],
  );

  // const onUpload = async (files: FileList | null) => {
  //   if (!files || files.length === 0) return;
  //   setBusy(true);
  //   setMsg(null);
  //   try {
  //     const fd = new FormData();
  //     Array.from(files).forEach((f) => fd.append("files", f));
  //
  //     await post("/images/upload", fd, {
  //       headers: { "Content-Type": "multipart/form-data" },
  //     });
  //     // await load();
  //     setLocalPreviews([]);
  //   } catch (e: any) {
  //     setMsg(e?.message ?? "upload failed");
  //     console.error(e);
  //   } finally {
  //     setBusy(false);
  //   }
  // };

  const onPickFiles = async (files: FileList | null) => {
    if (localPreviews.length >= maxFiles) {
      return;
    }

    if (!files || files.length === 0) return;

    const previews = Array.from(files)
      .slice(0, maxFiles - localPreviews.length)
      .map((f) => ({
        url: URL.createObjectURL(f),
        name: f.name,
        file: f,
      }));
    setLocalPreviews([...localPreviews, ...previews]);
    // await onUpload(files);
    // setPendingFiles(Array.from(files));
  };

  const onAnalyze = async () => {
    setBusy(true);
    setMsg(null);
    try {
      /* const r = await post("/images/analyze", {
        image_ids: selectedIds,
        topk: 3,
      });
      console.log("Analyze response:", r.data); */

      let idsToAnalyze = [...selectedIds];

      if (localPreviews.length > 0) {
        const fd = new FormData();
        localPreviews.forEach((f) => fd.append("files", f.file));
        const up = await post("/images/upload", fd, {
          headers: { "Content-Type": "multipart/form-data" },
        });

        const newIds: string[] = (up.data?.items ?? []).map(
          (it: ImgItem) => it.image_id,
        );

        idsToAnalyze = [...new Set([...idsToAnalyze, ...newIds])];

        // await load();
        // setLocalPreviews([]);
        // setPendingFiles([]);
      }

      // limit the number of analyzed photos to at most 5
      if (idsToAnalyze.length > 5) {
        setMsg(
          `You can analyze at most 5 images at a time (selected: ${idsToAnalyze.length}).`,
        );
        return;
      }

      if (idsToAnalyze.length === 0) {
        setMsg("Please select images or add files to analyze.");
        return;
      }
      const r = await post("/images/analyze", {
        image_ids: idsToAnalyze,
        topk: 3,
      });
      console.log("Analyze response:", r.data);

      //
      loadResult(idsToAnalyze.length).then(() => {
        setLocalPreviews([]);
      });
    } catch (e: any) {
      console.log("#x", e)
      setMsg(e?.message ?? "analyze failed");
    } finally {
      setBusy(false);
    }
  };

  // const toggleAll = () => {
  //   if (selectedIds.length === list.length) {
  //     setSel({});
  //   } else {
  //     const next: Record<string, boolean> = {};
  //     list.forEach((it) => (next[it.image_id] = true));
  //     setSel(next);
  //   }
  // };

  const clearSelection = () => {
    // setSel({});
    console.log("#XX")
    setLocalPreviews([]);
  }

  //
  const [historyItems, setHistoryItems] = useState<Item[]>([]);
  const loadResult = useCallback((len: number) => {
    // 初始化的时候不调整页面的页码
    return get("/history", {limit: len}).then(r => {
      setHistoryItems(r.data.items);
    }).catch(e => {
      console.log("load failed:", e);
    });
  }, []);

  // useEffect(() => {
  //   load("init");
  // }, []);

  const onDrop: React.DragEventHandler<HTMLDivElement> = async (e) => {
    e.preventDefault();
    if (busy) return;
    setDragOver(false);
    await onPickFiles(e.dataTransfer.files);
  };
  const onDragOver: React.DragEventHandler<HTMLDivElement> = (e) => {
    e.preventDefault();
    if (!dragOver) setDragOver(true);
  };
  const onDragLeave: React.DragEventHandler<HTMLDivElement> = () =>
    setDragOver(false);

  return (
    <div className="max-w-6xl mx-auto p-6">
      <div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">
        <div>
          <h1 className="text-2xl font-semibold text-white">
            Food Identification
          </h1>
          <p className="text-sm text-gray-400 mt-1">
            Welcome{user?.username ? `, ${user.username}` : ""}. Upload images,
            then select and analyze.
          </p>
        </div>
        <div className="flex items-center gap-3">
          {/*<button
            onClick={toggleAll}
            className="rounded-lg border border-white/15 bg-white/5 hover:bg-white/10 text-white px-3 py-2 text-sm"
          >
            {selectedIds.length === list.length && list.length > 0
              ? "Unselect all"
              : "Select all"}
          </button>*/}
          <button
            onClick={clearSelection}
            className="rounded-lg border border-white/15 bg-white/5 hover:bg-white/10 text-white px-3 py-2 text-sm"
            disabled={localPreviews.length === 0}
          >
            Clear
          </button>
          <button
            onClick={onAnalyze}
            disabled={
              busy ||
              (localPreviews.length === 0) ||
              localPreviews.length > 5
            }
            className="rounded-lg bg-indigo-500 px-4 py-2 text-sm font-semibold text-white hover:bg-indigo-400 disabled:opacity-40 disabled:cursor-not-allowed"
            title={
              localPreviews.length === 0
                ? "Select at least one image or add files"
                : localPreviews.length > 5
                  ? "You can analyze at most 5 images"
                  : "Analyze selected images"
            }
          >
            {busy ? (
              <span className="inline-flex items-center gap-2">
                <span className="h-4 w-4 animate-spin inline-block rounded-full border-2 border-white/60 border-t-transparent"></span>
                Analyzing…
              </span>
            ) : (
              "Analyze Selected"
            )}
          </button>
        </div>
      </div>

      <div className="mt-5">
        <div
          onDrop={onDrop}
          onDragOver={onDragOver}
          onDragLeave={onDragLeave}
          className={`relative rounded-2xl border-2 ${dragOver ? "border-indigo-400 bg-indigo-400/10" : "border-dashed border-white/15 bg-white/5"} p-6 transition`}
        >
          <div className="flex flex-col sm:flex-row sm:items-center gap-4">
            <div className="shrink-0 w-12 h-12 rounded-xl bg-indigo-500/20 flex items-center justify-center text-lg">
              📷
            </div>
            <div className="flex-1">
              <div className="text-white font-medium">Upload some images to get started.</div>
              <div className="text-xs text-gray-400">
                Click to choose or drag & drop JPG/PNG. Up to {maxFiles} pictures can be analyzed at one time.
              </div>
              {localPreviews.length > 0 && (
                <div className="text-xs text-emerald-300 mt-1">
                  {localPreviews.length} file(s) selected
                </div>
              )}
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => fileInputRef.current?.click()}
                className="rounded-lg bg-white/10 hover:bg-white/20 text-white px-3 py-2 text-sm"
                disabled={busy}
              >
                Choose files
              </button>
              <input
                ref={fileInputRef}
                type="file"
                multiple
                accept="image/*"
                onChange={(e) => onPickFiles(e.target.files)}
                className="hidden"
                disabled={busy}
              />
            </div>
          </div>
        </div>

        {localPreviews.length > 0 && (
          <div className="mt-4 grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {localPreviews.map((p, i) => (
              <div
                key={i}
                className="rounded-xl border border-white/15 bg-white/5 p-2"
              >
                <img
                  src={p.url}
                  alt={p.name}
                  className="w-full h-28 object-cover rounded"
                />
                <div
                  className="mt-2 text-xs text-gray-300 truncate"
                  title={p.name}
                >
                  {p.name}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      {msg && (
        <div className="mt-4 rounded-xl border border-red-500/30 bg-red-500/10 text-red-200 px-4 py-3 text-sm">
          {msg}
        </div>
      )}

      <div className="grid grid-cols-2 md:grid-cols-3 gap-6 mt-6">
        {historyItems && historyItems.map((it) => (<HistoryItem key={it.created_at} it={it} />))}
      </div>

      {/*<div className="mt-6">
        {list.length === 0 ? (
          <div className="rounded-2xl border border-white/10 bg-white/5 p-10 text-center text-gray-300">
            <div className="text-lg text-white mb-1">No images yet</div>
            <div className="text-sm text-gray-400">
              Upload some images to get started.
            </div>
          </div>
        ) : (
          <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
            {list.map((it) => {
              const checked = !!sel[it.image_id];
              return (
                <label
                  key={it.image_id}
                  className={`group relative block rounded-xl p-2 border ${checked ? "border-indigo-400 bg-indigo-400/10" : "border-white/10 bg-white/5 hover:border-white/20"} transition`}
                >
                  <div className="relative">
                    <img
                      src={`/uploads/${it.relative_path}`}
                      alt={it.original_name}
                      className="w-full h-36 object-cover rounded-lg"
                    />
                    <div
                      className={`absolute top-2 right-2 rounded-full px-2 py-1 text-[10px] font-semibold ${checked ? "bg-indigo-500 text-white" : "bg-black/40 text-gray-200"}`}
                    >
                      {checked ? "Selected" : "Select"}
                    </div>
                  </div>
                  <div className="mt-2 text-[12px] text-gray-300 flex flex-col gap-0.5">
                    <div className="truncate" title={it.original_name}>
                      {it.original_name}
                    </div>
                    <div className="text-gray-400">
                      {formatBytes(it.size)} · {formatDate(it.created_at)}
                    </div>
                  </div>
                  <input
                    type="checkbox"
                    className="sr-only"
                    checked={checked}
                    onChange={(e) =>
                      setSel((s) => ({ ...s, [it.image_id]: e.target.checked }))
                    }
                  />
                </label>
              );
            })}
          </div>
        )}
      </div>*/}
    </div>
  );
}
