
import { useEffect, useState } from "react";
import { get } from "~/net";
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts";
import HistoryItem, {type Item} from "~/component/history-item";


export default function HistoryRoute() {
  const [items, setItems] = useState<Item[]>([]);
  const [page, setPage] = useState(1);
  const [lastKey, setLastKey] = useState<any>(null);
  const [hasNext, setHasNext] = useState(true);

  const load = async (
    direction: "init" | "next" | "prev" = "init",
    key?: any
  ) => {
    try {
      // 初始化的时候不调整页面的页码
      const params: any = {limit: 8};
      if (direction === "next" && key)
        params.last_key = JSON.stringify(key);

      const r = await get("/history", params);
      setItems(r.data.items);
      r.data.last_evaluated_key ? setHasNext(true) : setHasNext(false);
      setLastKey(r.data.last_evaluated_key);


      if (direction === "next") setPage((p) => p + 1);
      else if (direction === "prev") setPage((p) => Math.max(1, p - 1));

    } catch (e: any) {
      console.log("load failed:", e);
    }
  };

  useEffect(() => {
    load("init");
  }, []);

  console.log(">>> items:", items);

  return (
    <div className="max-w-6xl mx-auto p-6">
      {/*<div className="flex flex-col sm:flex-row sm:items-end sm:justify-between gap-4">*/}
      <h1 className="text-2xl font-semibold text-white">History</h1>
      <div className="py-5">
        <button
          onClick={()  => load("prev")}
          disabled={page === 1}
          className="px-3 py-1 rounded bg-white/10 text-white disabled:opacity-40">Prev
        </button>
        <span className="mx-2 text-white text-sm">Page {page}</span>
        <button
          onClick={() => load("next", lastKey)}
          disabled={!hasNext}
          className="px-3 py-1 rounded bg-white/10 text-white disabled:opacity-40">Next
        </button>
      </div>

      <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
        {items.map((it) => (<HistoryItem key={it.created_at} it={it} />))}
      </div>
    </div>
  );
}
