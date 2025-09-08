
import { useEffect, useState } from "react";
import { get } from "~/net";
import { PieChart, Pie, Cell, Tooltip, Legend, ResponsiveContainer } from "recharts";

type Item = {
  image_id: string;
  label: string;
  score: number;
  created_at: number;
  nutrition: {
    protein_g: string;
    fat_g: string;
    carbs_g: string;
    energy_kcal: string;
    name: string;
  };
  image_url?: string; 
};



const COLORS = ["#0088FE", "#00C49F", "#FFBB28", "#FF8042", "#D0D0D0"];

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
    const params: any = { limit: 4 };
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

  // AI想的归纳方法，不知道原理是什么
  /* 把 4 大项 + 其他 转成饼图需要的数据 */
  const toPieData = (n: Item["nutrition"]) => {
    const p = Number(n.protein_g);
    const f = Number(n.fat_g);
    const c = Number(n.carbs_g);
    const e = Number(n.energy_kcal); // kcal
    // 用能量近似占比：蛋白质 4 kcal/g，脂肪 9 kcal/g，碳水 4 kcal/g
    const pE = p * 4;
    const fE = f * 9;
    const cE = c * 4;
    const otherE = Math.max(0, e - (pE + fE + cE));
    const total = pE + fE + cE + otherE || 1;
    return [
      { name: "Protein", value: +((pE / total) * 100).toFixed(1) },
      { name: "Fat", value: +((fE / total) * 100).toFixed(1) },
      { name: "Carbohydrates", value: +((cE / total) * 100).toFixed(1) },
      { name: "Other", value: +((otherE / total) * 100).toFixed(1) },
    ];
  };
  console.log(">>> items:", items);

  return (
    <div className="max-w-[1350px] mx-auto p6">
      <h1 className="text-2xl font-bold mb-4">History</h1>
       <button
        onClick={() => load("prev")}
        disabled={page === 1}
        className="px-3 py-1 rounded bg-white/10 text-white disabled:opacity-40"
      >
        Prev
      </button>
      <span className="mx-2 text-white text-sm">Page {page}</span>
      <button
        onClick={() => load("next", lastKey)}
        disabled={!hasNext}
        className="px-3 py-1 rounded bg-white/10 text-white disabled:opacity-40"
      >
        Next
      </button>
      <div className="grid grid-cols-2 md:grid-cols-4 gap-6">
        {items.map((it) => {
          const pieData = toPieData(it.nutrition);
          return (
          <div
            key={it.created_at}
            className="rounded-xl shadow border p-4 bg-white flex flex-col min-h-[420px]"
          >
   
            <div className="mb-3">
              <img
                src={`/uploads/${it.image_url}`}
                alt={it.label}
                className="w-full h-48 object-contain rounded-t"
              />
              {/* 模型识别出来的名字 */}
              <div className="bg-black/60 text-white text-sm px-3 py-1 rounded-b">
                {it.label}
              </div>
            </div>

            {/* 日期和相似度 */}
            <div className="text-sm text-gray-500 mb-2">
              Similarity {(it.score * 100).toFixed(1)}% ·{" "}
              {new Date(it.created_at).toLocaleString()}
            </div>
            {/* 归纳后的种类 */}
            <div className="flex justify-center gap-5 text-xs mb-3">
              {[
                { name: 'Protein', color: COLORS[0] },
                { name: 'Fat',  color: COLORS[1] },
                { name: 'Carbohydrates', color: COLORS[2] },
                { name: 'Other', color: COLORS[3] },
              ].map((item) => (
                <div key={item.name} className="flex items-center gap-1">
                  <span
                    className="inline-block w-3 h-3 rounded"
                    style={{ backgroundColor: item.color }}
                  />
                  <span style={{ color: item.color }} className="font-medium">
                    {item.name}
                  </span>
                </div>
              ))}
            </div>

            {/* 饼图 */}
            <div className="flex-1">
              <ResponsiveContainer width="100%" height={200}>
                <PieChart>
                  <Pie
                    data={pieData}
                    dataKey="value"
                    nameKey="name"
                    cx="50%"
                    cy="50%"
                    outerRadius={70}
                  >
                    {pieData.map((_, idx) => (
                      <Cell key={idx} fill={COLORS[idx % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip
                    contentStyle={{ whiteSpace: 'normal' }}
                    formatter={(v) => [`${v}%`, 'Proportion']}
                  />
                </PieChart>
              </ResponsiveContainer>
            </div>
          </div>
          );
      })}
      </div>
    </div>
  );
}


