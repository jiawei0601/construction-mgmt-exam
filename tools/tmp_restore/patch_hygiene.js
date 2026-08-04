global.window = {};
require('../../data/hygiene-questions.js');
const fs = require('fs');
const d = window.EXAM_DATA;

function empty4() { return {"1":"","2":"","3":"","4":""}; }

const newBank = [
  {id:"b-03-038", stem:"下列何者為我國職業安全衛生法規之機械設備器具驗證合格標章？",
   options: empty4(), answer:["1"], img:"assets/img/hygiene/b-03-038.png",
   appearances:[{year:"109",session:2,no:4},{year:"110",session:2,no:44}]},
  {id:"b-03-039", stem:"下列何者為我國職業安全衛生法規之機械設備器具安全標示？",
   options: empty4(), answer:["4"], img:"assets/img/hygiene/b-03-039.png",
   appearances:[]},
  {id:"b-03-054", stem:"下列何種危害性化學品一般不會使用如下圖式？",
   options:{"1":"壓縮氣體","2":"液化氣體","3":"溶解氣體","4":"冷凍氣膠"}, answer:["4"],
   img:"assets/img/hygiene/b-03-054.png", appearances:[]},
  {id:"b-03-055", stem:"何種危害性化學品一般會使用如下圖式？",
   options:{"1":"易燃液體","2":"易燃氣膠","3":"氧化性液體","4":"金屬腐蝕物"}, answer:["3"],
   img:"assets/img/hygiene/b-03-055.png", appearances:[{year:"112",session:2,no:22}]},
  {id:"b-03-056", stem:"下列何種危害性化學品一般不會使用如下圖式？",
   options:{"1":"急毒性物質：吞食","2":"急毒性物質：皮膚","3":"急毒性物質：吸入","4":"致癌物質"}, answer:["4"],
   img:"assets/img/hygiene/b-03-056.png", appearances:[{year:"107",session:3,no:40}]},
  {id:"b-03-057", stem:"何種危害性化學品一般不會使用如下圖式？",
   options:{"1":"生殖毒性物質","2":"腐蝕／刺激皮膚物質","3":"急毒性物質：吸入","4":"致癌物質"}, answer:["2"],
   img:"assets/img/hygiene/b-03-057.png",
   appearances:[{year:"112",session:2,no:44},{year:"114",session:"2颱風延期考區",no:27},{year:"114",session:3,no:13}]},
  {id:"b-03-058", stem:"下列何種危害性化學品一般不會使用如下圖式？",
   options:{"1":"腐蝕／刺激皮膚物質","2":"皮膚過敏物質","3":"急毒性物質：吸入","4":"爆炸物"}, answer:["4"],
   img:"assets/img/hygiene/b-03-058.png", appearances:[{year:"114",session:1,no:27}]},
  {id:"b-03-059", stem:"下列何種危害性化學品一般不會使用如下圖式？",
   options:{"1":"易燃氣體","2":"易燃液體","3":"金屬腐蝕物","4":"易燃氣膠"}, answer:["3"],
   img:"assets/img/hygiene/b-03-059.png", appearances:[]},
  {id:"b-03-060", stem:"下列何種危害性化學品一般不會使用如下圖式？",
   options:{"1":"腐蝕／刺激皮膚物質","2":"致癌物質","3":"嚴重損傷／刺激眼睛物質","4":"金屬腐蝕物"}, answer:["2"],
   img:"assets/img/hygiene/b-03-060.png", appearances:[{year:"108",session:2,no:9}]},
  {id:"b-03-062", stem:"當處置使用具有如下圖式之危害性化學品時，不宜採取何措施？",
   options:{"1":"以鐵器敲打攪拌","2":"遠離熱源","3":"避免震動","4":"操作時穿著防易產生靜電之衣服鞋具"}, answer:["1"],
   img:"assets/img/hygiene/b-03-062.png", appearances:[{year:"113",session:2,no:2}]},
  {id:"b-03-063", stem:"當處置使用具有如下圖式之危害性化學品時，不宜採取何措施？",
   options:{"1":"廢液倒入廢液桶中","2":"操作時穿戴合適之個人防護具","3":"用剩之化學品以水稀釋後直接倒入排水溝","4":"依SOP操作"}, answer:["3"],
   img:"assets/img/hygiene/b-03-063.png",
   appearances:[{year:"107",session:1,no:38},{year:"111",session:3,no:54},{year:"113",session:1,no:31}]},
  {id:"b-03-258", stem:"有一酸洗槽上有懸吊式氣罩，酸洗槽作業面周長18公尺，其與氣罩間垂直高度差為3公尺，若氣罩寬3.75公尺，長6公尺，捕捉風速平均為7.5m/s，其理論排氣量為X。若其為加強補集效果，在氣罩下多加三片塑膠版，圍住三面，僅餘一長面操作，則理論排氣量為Y。下列何者正確？",
   options:{"1":"X<Y","2":"X=Y","3":"Y=135m³/s","4":"X=844m³/s"}, answer:["3"],
   appearances:[{year:"114",session:3,no:30}]},
];

const newSubject = [
  {id:"s-108-3-028", stem:"下列何者為我國職安法規之機械設備安全標章？",
   options: empty4(), answer:["2"], img:"assets/img/hygiene/s-108-3-028.png",
   appearances:[{year:"108",session:3,no:28},{year:"110",session:1,no:39}]},
  {id:"s-107-2-049", stem:"下列何種危害性化學品一般會使用如下圖式？",
   options:{"1":"易燃氣膠","2":"易燃液體","3":"金屬腐蝕物","4":"氧化性液體"}, answer:["4"],
   img:"assets/img/hygiene/s-107-2-049.png",
   appearances:[{year:"107",session:2,no:49},{year:"108",session:1,no:28},{year:"108",session:3,no:41}]},
  {id:"s-109-1-023", stem:"下列何者為我國職安法規之機械設備驗證合格標章？",
   options: empty4(), answer:["3"], img:"assets/img/hygiene/s-109-1-023.png",
   appearances:[{year:"109",session:1,no:23}]},
  {id:"s-112-1-046", stem:"下列何種危害性化學品一般不會使用如下圖式？",
   options:{"1":"生殖毒性物質","2":"急毒性物質：吸入","3":"致癌物質","4":"腐蝕／刺激皮膚物質"}, answer:["4"],
   img:"assets/img/hygiene/s-112-1-046.png", appearances:[{year:"112",session:1,no:46}]},
  {id:"s-113-3-021", stem:"有一酸洗槽上有懸吊式氣罩，酸洗槽作業面周長18公尺，其與氣罩間垂直高度差為3公尺，若氣罩寬3.75公尺，長6公尺，捕捉風速平均為7.5m/s，其理論排氣量為X。若其為加強捕集效果，在氣罩下多加三片塑膠版，圍住三面，僅餘一長面操作，則理論排氣量為Y。請問下列那一項正確？",
   options:{"1":"X<Y","2":"X=844m³/s","3":"X=Y","4":"Y=135m³/s"}, answer:["4"],
   appearances:[{year:"113",session:3,no:21}]},
];

function fill(obj, category, subject) {
  return Object.assign({id: obj.id, category, subject, type:"single", stem: obj.stem},
    obj.img ? {img: obj.img} : {},
    {options: obj.options, answer: obj.answer, appearances: obj.appearances});
}

const bankFilled = newBank.map(o => fill(o, "professional", "工作項目03 專業課程"));
const subjFilled = newSubject.map(o => fill(o, "professional", "職業衛生管理甲級"));

// sanity: none of these ids already exist
for (const o of [...bankFilled, ...subjFilled]) {
  if (d.questions.find(x => x.id === o.id)) throw new Error("DUPLICATE ID " + o.id);
}

// insert bank entries into b- section (sorted), subject entries into s- section (sorted)
const firstS = d.questions.findIndex(x => x.id.startsWith('s-'));
const firstC = d.questions.findIndex(x => x.id.startsWith('c-'));

let bSection = d.questions.slice(0, firstS);
let sSection = d.questions.slice(firstS, firstC);
let cSection = d.questions.slice(firstC);

bSection = bSection.concat(bankFilled).sort((a,b) => a.id.localeCompare(b.id));
sSection = sSection.concat(subjFilled).sort((a,b) => a.id.localeCompare(b.id));

// update existing c- entries
const c1 = cSection.find(x => x.id === 'c-90008-013');
c1.appearances.push({year:"109",session:2,no:9});
const c2 = cSection.find(x => x.id === 'c-90009-002');
c2.appearances.push({year:"107",session:1,no:43},{year:"111",session:2,no:30},{year:"112",session:1,no:31});

const finalQuestions = [...bSection, ...sSection, ...cSection];
console.log("total before:", d.questions.length, "after:", finalQuestions.length);

const out = { meta: d.meta, questions: finalQuestions };

let text = JSON.stringify(out, null, 2);
text = text.split("\n").join("\r\n");
const header = "// 職業衛生管理甲級 題庫資料（自動產生，來源見 meta.sources；解析報告見 data/HYGIENE_PARSE_REPORT.md）\r\n// schema 與 data/questions.js 一致\r\nwindow.EXAM_DATA = ";
fs.writeFileSync("data/hygiene-questions.js", header + text + ";\r\n");
console.log("written");
