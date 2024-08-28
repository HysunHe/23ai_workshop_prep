向量基本操作：

L2:
SELECT VECTOR_DISTANCE( vector('[2,2]'), vector('[5,6]'), EUCLIDEAN ) as distance;

COSINE:
SELECT VECTOR_DISTANCE( vector('[2,2]'), vector('[5,5]'), COSINE ) as distance;


建表：
drop table lab_vecstore_hysun cascade constraints purge;

CREATE TABLE lab_vecstore_hysun (
    id VARCHAR2(50) DEFAULT SYS_GUID() PRIMARY KEY,
    dataset_name VARCHAR2(50) NOT NULL,
    document CLOB,
    cmetadata JSON,
    embedding VECTOR(*, FLOAT32)
);

CREATE TABLE <表名> (
    id VARCHAR2(50) DEFAULT SYS_GUID() PRIMARY KEY,
    dataset_name VARCHAR2(50) NOT NULL,
    document CLOB,
    cmetadata JSON,
    embedding VECTOR(*, FLOAT32)
);

select * from lab_vecstore_hysun;

select document, embedding, json_value(cmetadata, '$.source') as src_file from lab_vecstore_hysun;

初始化数据：

curl -X 'POST' 
  'http://localhost:18000/workshop/prepare-data' 
  -H 'accept: application/json' 
  -H 'Content-Type: application/json' 
  -d '{
  "table_name": "<表名>",
  "dataset_name": "oracledb_docs"
}'

curl -X 'POST' 
  'http://localhost:18000/workshop/embedding' 
  -H 'accept: application/json' 
  -H 'Content-Type: application/json' 
  -d '"Oracle 23ai 新特性"'


-- Index: https://docs.oracle.com/en/database/oracle/oracle-database/23/vecse/oracle-ai-vector-search-users-guide.pdf
-- https://learn.microsoft.com/en-us/javascript/api/@azure/search-documents/hnswparameters?view=azure-node-latest

HNSW:

https://cloud.tencent.com/developer/article/2436455

M：这是构建索引时每个层次的最大边数。M的值越大，索引的内存消耗越大，但查询时的精度可能更高。

Within the maximum number of connections (NEIGHBORS) permitted per vector

The number of bi-directional links created for every new element during construction. Increasing this parameter value may improve recall and reduce retrieval times for datasets with high intrinsic dimensionality at the expense of increased memory consumption and longer indexing time.

efConstruction：这是构建索引时的搜索路径的长度。efConstruction的值越大，构建索引时的时间消耗越长，但查询时的精度可能更高。
The maximum number of closest vector candidates considered at each step of the search during insertion (EFCONSTRUCTION)

The size of the dynamic list containing the nearest neighbors, which is used during index time. Increasing this parameter may improve index quality, at the expense of increased indexing time. At a certain point, increasing this parameter leads to diminishing returns.

CREATE VECTOR INDEX galaxies_hnsw_idx ON galaxies (embedding) 
ORGANIZATION INMEMORY NEIGHBOR GRAPH
DISTANCE COSINE
WITH TARGET ACCURACY 90 
PARAMETERS (type HNSW, neighbors 8, efconstruction 50)
parallel 2;


SELECT INDEX_NAME, INDEX_TYPE, INDEX_SUBTYPE FROM USER_INDEXES;

INDEX_NAME INDEX_TYPE INDEX_SUBTYPE
-------------- ----------- -----------------------------
GALAXIES_HNSW_IDX VECTOR INMEMORY_NEIGHBOR_GRAPH_HNSW

SELECT JSON_SERIALIZE(IDX_PARAMS returning varchar2 PRETTY) FROM VECSYS.VECTOR$INDEX where IDX_NAME = 'GALAXIES_HNSW_IDX';

JSON_SERIALIZE(IDX_PARAMSRETURNINGVARCHAR2PRETTY)
____________________________________________________


EXPLAIN PLAN FOR
SELECT name，VECTOR_DISTANCE(embedding, to_vector('[0,1,1,0,0]'), COSINE ) as distance
FROM galaxies
ORDER BY distance
FETCH APPROX FIRST 4 ROWS ONLY;

select plan_table_output from table(dbms_xplan.display('plan_table',null,'all'));


IVF:

NEIGHBOR PARTITIONS determines the target number of centroid partitions that are created
by the index.

CREATE VECTOR INDEX galaxies_ivf_idx ON galaxies (embedding) 
ORGANIZATION NEIGHBOR PARTITIONS
DISTANCE COSINE
WITH TARGET ACCURACY 90 
PARAMETERS (type IVF, neighbor partitions 8)
parallel 2;

SELECT INDEX_NAME, INDEX_TYPE, INDEX_SUBTYPE FROM USER_INDEXES;

INDEX_NAME INDEX_TYPE INDEX_SUBTYPE
-------------- ----------- -----------------------------
GALAXIES_IVF_IDX VECTOR NEIGHBOR_PARTITIONS_IVF

SELECT JSON_SERIALIZE(IDX_PARAMS returning varchar2 PRETTY) FROM VECSYS.VECTOR$INDEX where IDX_NAME = 'GALAXIES_IVF_IDX';

JSON_SERIALIZE(IDX_PARAMSRETURNINGVARCHAR2PRETTY)
____________________________________________________

EXPLAIN PLAN FOR
SELECT /*+ VECTOR_INDEX_TRANSFORM(galaxies GALAXIES_IVF_IDX pre_filter_without_join_back) */ name，VECTOR_DISTANCE(embedding, to_vector('[0,1,1,0,0]'), COSINE ) as distance
FROM galaxies
ORDER BY distance
FETCH APPROX FIRST 2 ROWS ONLY;

SQL> select plan_table_output from table(dbms_xplan.display('plan_table',null,'all'));

EXPLAIN PLAN FOR
SELECT /*+ VECTOR_INDEX_TRANSFORM(galaxies GALAXIES_IVF_IDX pre_filter_with_join_back) */ name，VECTOR_DISTANCE(embedding, to_vector('[0,1,1,0,0]'), COSINE ) as distance
FROM galaxies
ORDER BY distance
FETCH APPROX FIRST 2 ROWS ONLY;

EXPLAIN PLAN FOR
SELECT /*+ VECTOR_INDEX_TRANSFORM(galaxies GALAXIES_IVF_IDX) */ name，VECTOR_DISTANCE(embedding, to_vector('[0,1,1,0,0]'), COSINE ) as distance
FROM galaxies
ORDER BY distance
FETCH APPROX FIRST 3 ROWS ONLY;



CREATE VECTOR INDEX lab_ivf_idx ON lab_vecstore_hysun (embedding) 
ORGANIZATION NEIGHBOR PARTITIONS
DISTANCE COSINE
WITH TARGET ACCURACY 90 
PARAMETERS (type IVF, neighbor partitions 32)
parallel 2;

CREATE VECTOR INDEX lab_hnsw_idx ON lab_vecstore_hysun (embedding) 
ORGANIZATION INMEMORY NEIGHBOR GRAPH
DISTANCE COSINE
WITH TARGET ACCURACY 90 
PARAMETERS (type HNSW, neighbors 8, efconstruction 50)
parallel 2;


curl -X 'POST' \
  'http://localhost:18000/workshop/embedding' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '"Oracle 23ai 新特性"'



select document, json_value(cmetadata, '$.source') as src_file 
from lab_vecstore
where dataset_name='oracledb_docs'
order by VECTOR_DISTANCE(embedding, to_vector('[0.8165184855461121, 0.9929913878440857, 0.60514235496521, 0.9156814217567444, -0.4184103310108185, 0.6279500126838684, 0.27528947591781616, 0.09972244501113892, -1.0412068367004395, 0.7242997884750366, -0.0019543981179594994, -0.41787368059158325, 2.0671145915985107, -0.6989288926124573, 0.3267768323421478, -0.8929062485694885, -1.4247781038284302, 0.3772987127304077, 0.9484530091285706, 0.7480047941207886, 0.3293590545654297, -0.9412945508956909, 0.10091835260391235, -0.5925852060317993, -0.2065550982952118, 0.3209895193576813, 1.0987961292266846, 1.3331555128097534, 0.3581351637840271, -0.9019574522972107, 0.5417171120643616, -1.3484156131744385, 2.163388729095459, 0.9760211110115051, -0.24661321938037872, 0.9272908568382263, -0.011589903384447098, -0.29004088044166565, -1.2046431303024292, 0.918506383895874, -0.06750181317329407, -1.1451847553253174, 1.256298303604126, -0.1572350710630417, 0.4913124442100525, -0.11192450672388077, -0.4175677001476288, 0.6475199460983276, -0.3774612545967102, -0.6863062977790833, -0.42848700284957886, 0.5514025092124939, 0.6829992532730103, -0.7318109273910522, 0.22573280334472656, 1.2264033555984497, 1.0222032070159912, 0.44344645738601685, 0.0455365888774395, -0.7276411652565002, -0.9325190186500549, 2.6146340370178223, -0.8470523357391357, 0.8836098313331604, 0.6071594953536987, 0.5305112600326538, -0.12606565654277802, -0.2375195175409317, 1.713836908340454, 1.419414758682251, -1.2088189125061035, 2.427159547805786, -0.19737474620342255, -1.2152187824249268, -0.4890981912612915, 0.4966585040092468, 0.5265249013900757, 0.05154818296432495, -1.354767084121704, -0.7629138231277466, 1.695274829864502, -0.17230477929115295, 0.3944135308265686, -0.05677884817123413, 1.1698483228683472, 0.025691822171211243, 0.13813647627830505, 3.5681345462799072, 1.3602676391601562, 0.5438013076782227, -0.08622045814990997, 0.48611006140708923, 0.5864006280899048, -0.2592349648475647, -0.579928457736969, -0.5487643480300903, -0.35110583901405334, 1.127042531967163, 1.4000544548034668, -1.189772367477417, 0.15701276063919067, -0.5543661713600159, -0.44776982069015503, -0.8500083088874817, 0.20887237787246704, -1.0472840070724487, 0.8341460227966309, 0.25730597972869873, 0.220865860581398, 1.0516316890716553, 1.17168390750885, 1.0871564149856567, -0.29089608788490295, 1.015012502670288, 0.3555355966091156, 0.7077906131744385, 1.2562373876571655, -0.18970921635627747, -1.018487572669983, 0.21158641576766968, 0.34846457839012146, 0.010949674993753433, 1.1654810905456543, -1.8110883235931396, -0.24423760175704956, -0.23444682359695435, -0.2652791738510132, 0.48318567872047424, 0.8749096989631653, -0.32638123631477356, -0.8245049118995667, -0.299204558134079, -0.18257661163806915, -0.13283559679985046, 0.3701237440109253, -1.0194511413574219, -0.6040478944778442, -0.20016422867774963, 0.27570903301239014, 0.7515652179718018, 0.35190898180007935, -0.6113996505737305, 0.8278483748435974, 0.36033275723457336, 0.3573731482028961, 0.008063742890954018, -0.11801108717918396, -0.7183032035827637, 1.2688475847244263, 0.9687840342521667, 0.8697808384895325, -0.029141023755073547, 0.5633946657180786, -0.24772398173809052, 0.43023642897605896, -0.6206769943237305, 1.0322281122207642, -0.46447357535362244, -0.059244900941848755, -0.26544085144996643, 0.5594695210456848, -0.51436448097229, 1.0023822784423828, 0.21863527595996857, -0.37556684017181396, -0.7632661461830139, -0.041058383882045746, -0.7251375913619995, 0.0006007812917232513, 1.264998435974121, -0.009682945907115936, 0.9356796741485596, 0.9438220262527466, 1.0360639095306396, 0.22180184721946716, -0.2642703950405121, 0.6447533369064331, 1.4934459924697876, -0.1547030508518219, 0.8326311111450195, 0.5580376386642456, -0.9272060394287109, 0.19704076647758484, -1.3669764995574951, -1.4627245664596558, 0.30487194657325745, -1.3494000434875488, 0.4675583839416504, -0.10426271706819534, 0.15248717367649078, 0.5611053705215454, 1.3280178308486938, 1.1858839988708496, -0.2819743752479553, -0.05289234220981598, 1.0067150592803955, 0.19286848604679108, -0.5377382040023804, 0.11353790760040283, 0.4240384101867676, 0.3964574933052063, -2.373746871948242, 0.5405543446540833, 0.4351179599761963, 1.2262367010116577, 0.09461881965398788, 0.45582470297813416, 0.1581001728773117, -0.37766021490097046, -1.0063191652297974, 0.4805070161819458, 0.1379634141921997, 1.3120120763778687, -0.4276597499847412, 1.4165525436401367, 0.17374806106090546, -0.4364038407802582, -1.091676950454712, 0.19115881621837616, -0.6495493650436401, 0.19049635529518127, 0.5146724581718445, -0.18828296661376953, -0.06570414453744888, 0.6487032771110535, 0.42129963636398315, -0.09523752331733704, 1.4799213409423828, -0.07370859384536743, 0.17574694752693176, -0.062412992119789124, 0.9712915420532227, 0.4537895917892456, -0.21675629913806915, -0.850211501121521, 0.6403552889823914, -0.3157779574394226, -0.15826106071472168, -0.9663159847259521, -1.0669821500778198, -0.1982014775276184, 1.7123159170150757, -1.9750157594680786, 0.4497857391834259, -1.7126820087432861, 1.2746285200119019, -0.9603769779205322, 0.895435094833374, -1.137880563735962, -0.2467912882566452, 0.16447554528713226, -1.017038106918335, 0.3032487630844116, -1.8022345304489136, -1.0040287971496582, 0.5378794074058533, -1.5576226711273193, -0.18299806118011475, 0.5153221487998962, 0.13660551607608795, 1.0120173692703247, -0.39845797419548035, -0.15290547907352448, -0.44973739981651306, 0.6440964937210083, -0.12564212083816528, 0.3042004406452179, -0.7600468397140503, 0.17099082469940186, 1.295818567276001, -0.5694224834442139, 0.8509036898612976, 0.5209811925888062, -0.21731869876384735, -0.9130775928497314, -0.40369123220443726, 0.020742081105709076, 1.319621205329895, -0.4634562134742737, 1.7779123783111572, -1.003603219985962, 2.015103816986084, -0.18348422646522522, -0.025224529206752777, 2.1450397968292236, -0.5381225347518921, 0.41226926445961, 1.0085959434509277, 1.5142357349395752, -0.5382359027862549, -0.6864888072013855, 0.020722761750221252, 0.10366520285606384, -0.14850062131881714, -0.36341220140457153, 1.7823576927185059, -1.1649075746536255, -0.11387551575899124, 0.671761155128479, 1.0765434503555298, -0.011426825076341629, 1.1794040203094482, -0.5229810476303101, -1.0284253358840942, 0.28744423389434814, 0.8430193662643433, 0.7375212907791138, 0.7130423784255981, -0.2953542470932007, -1.2114734649658203, -0.922247588634491, 0.03383459523320198, -0.29597580432891846, 0.7053042054176331, 0.33319130539894104, -0.2728145122528076, 0.5572952032089233, -0.4616488814353943, -0.39925724267959595, 0.24495381116867065, -0.21519598364830017, -0.3344627320766449, 0.031279802322387695, 0.33500733971595764, -0.9834286570549011, 1.718810796737671, 0.3037411570549011, -1.0776818990707397, -0.5341043472290039, 0.3655340373516083, -0.8862850069999695, -0.1640588641166687, -0.004321187734603882, -0.6552742719650269, 0.6642345190048218, -0.1610734611749649, -0.24448497593402863, -0.28832730650901794, -0.5137307047843933, 0.7499560713768005, 0.6847479343414307, -0.6288416385650635, 0.14086371660232544, -0.3195434510707855, 1.9461231231689453, -0.2265709936618805, 1.627565622329712, -0.664673924446106, -0.032998282462358475, -0.3713313341140747, -0.27906620502471924, 0.10544805973768234, 0.5681121945381165, 0.38053300976753235, 0.06441422551870346, 0.1764446198940277, 0.6186070442199707, -0.20498138666152954, 0.2515856921672821, 0.5712647438049316, 0.4626525342464447, -0.9879912734031677, 0.22725757956504822, -0.09812690317630768, -0.16513726115226746, 0.6680848598480225, -0.016946638002991676, 0.2730339467525482, 0.7636468410491943, -0.4925047755241394, -0.035910576581954956, 0.6295747756958008, 0.38027656078338623, -0.41231876611709595, -2.2738890647888184, 0.5412936210632324, 0.4076313376426697, -0.08621599525213242, 0.0482138954102993, 0.2593461275100708, -0.03484318405389786, 0.41939252614974976, 0.3824058175086975, -0.2511245608329773, -1.191136121749878, -1.0080264806747437, 0.8084449768066406, -1.2765460014343262, 0.07979119569063187, -0.5811314582824707, -0.7472550272941589, 0.18762849271297455, 0.9452218413352966, -0.7420617341995239, -0.9852816462516785, -0.9812008142471313, -0.8435315489768982, 0.4827592670917511, 0.09639552235603333, -0.6444871425628662, 0.5351474285125732, 0.31876683235168457, -1.2380573749542236, 0.3563944697380066, 0.7059497833251953, 0.5915079116821289, 0.3785375952720642, 1.0199254751205444, 1.302288293838501, -0.23470206558704376, 0.7180806398391724, 0.5084434747695923, -0.6587988138198853, -0.6371639370918274, 0.10101950913667679, -1.5107399225234985, -0.9410131573677063, -0.7397129535675049, -0.6583808064460754, -0.6464521288871765, -0.40377599000930786, -0.2500501275062561, 0.7905325889587402, 1.433401346206665, -0.8276887536048889, -0.7224894762039185, -0.68577641248703, -0.7711609601974487, -0.05055709183216095, 2.3560028076171875, 0.34361815452575684, 2.021899700164795, -0.0031795017421245575, 0.7387228608131409, 0.2837420403957367, 1.0256383419036865, 0.6144429445266724, 0.25582247972488403, 0.2546999752521515, 0.1424260139465332, -0.4267612099647522, -0.1083868145942688, -1.4996590614318848, -2.033827781677246, 0.9156992435455322, -1.0536727905273438, 0.4303370416164398, -1.3349685668945312, -0.1215612068772316, -1.6433513164520264, 1.3724497556686401, -0.6232020258903503, -1.906252145767212, 0.9940755367279053, 1.1080719232559204, -0.23436997830867767, 1.3294970989227295, -0.6296367049217224, -0.1559264212846756, 1.0517032146453857, -0.2091563493013382, 0.7238271832466125, -0.5097934603691101, -0.750045895576477, -0.5672898888587952, 0.4363716244697571, -1.036797285079956, 1.1688218116760254, -1.1192234754562378, 0.53874671459198, 0.5268548130989075, -1.0989888906478882, 0.3346653878688812, 0.4679454565048218, -0.20885853469371796, 0.17840199172496796, 1.0852246284484863, 0.28819552063941956, -0.9752291440963745, -1.440722942352295, 1.132613182067871, -0.5376721024513245, -0.14669518172740936, -0.12843766808509827, -1.6355140209197998, 0.6958316564559937, -0.15799467265605927, 0.6232339143753052, -1.20824134349823, 0.4284075200557709, 0.7266727089881897, -0.14151814579963684, -0.1359313577413559, -0.3136380910873413, 0.5327268242835999, 0.5464619994163513, -0.034475721418857574, -0.14944346249103546, -0.6282007694244385, 1.3585466146469116, 0.37592586874961853, -0.564229428768158, -0.5099148750305176, -0.6823380589485168, -0.15082120895385742, 0.76546311378479, 0.0685625895857811, 0.5496315956115723, -0.24779292941093445, 2.0462608337402344, 1.373731017112732, 0.40920117497444153, -1.698513150215149, 2.014063835144043, 0.5211402773857117, -1.518532395362854, 1.1921119689941406, -0.41341274976730347, -0.26004892587661743, -1.2231988906860352, 0.2879779636859894, -0.8626695275306702, 0.5570862889289856, 1.5888590812683105, 0.46983620524406433, -0.707183837890625, -0.262201726436615, -1.1781120300292969, 0.4664878845214844, -0.3998006582260132, -0.9209334850311279, -0.07918305695056915, -0.015438541769981384, 0.7970162034034729, 0.5427157878875732, -0.2865583598613739, 2.4779818058013916, 0.7703176140785217, 0.41694340109825134, -0.5382050275802612, -0.9130071997642517, -0.14510074257850647, 1.249776005744934, 0.8869608640670776, -0.9172533750534058, -0.5609655976295471, -0.5999096035957336, 0.37553033232688904, 1.222050428390503, 0.24796025454998016, -0.8769406080245972, 1.2141362428665161, 0.4538317024707794, -0.4031752645969391, -0.8919470310211182, 0.11548849940299988, -0.895746111869812, -0.6062198281288147, 0.8049734830856323, -1.4351204633712769, 0.016576383262872696, 0.12358851730823517, -0.4807448089122772, -1.1567673683166504, -1.7363077402114868, -1.044687032699585, -0.10642991960048676, -0.23576122522354126, -0.781344473361969, -0.9195950031280518, 0.3899392783641815, -0.16162441670894623, 0.4166380763053894, -1.2300400733947754, -1.525693416595459, 0.9391961693763733, -0.9152942299842834, 0.32649528980255127, -0.8943911790847778, -0.9059198498725891, -0.5721795558929443, -0.07067511975765228, 0.5402684807777405, -0.5289252996444702, 0.08945460617542267, -0.6383883953094482, 0.7139982581138611, -1.5605571269989014, -1.2983993291854858, -0.2380162477493286, -1.4184091091156006, -0.8033026456832886, -0.6108459830284119, 0.22067242860794067, 0.8441752195358276, -0.8977459073066711, 0.10630909353494644, -1.061100721359253, 1.2807259559631348, -0.09081070125102997, -0.34853044152259827, -0.43503543734550476, 1.1024916172027588, -0.4055477976799011, -1.1039633750915527, -0.20587283372879028, -0.37723422050476074, 0.09703638404607773, 1.3456183671951294, 0.5161638259887695, -0.46709269285202026, -0.1486879289150238, -1.1250497102737427, 0.8032416701316833, -1.40120267868042, -0.790279746055603, -0.634344756603241, -0.4832894802093506, -1.3399492502212524, 0.8898983001708984, 0.27308255434036255, -0.38442909717559814, -0.5928069949150085, -0.27717822790145874, -0.22719122469425201, -0.19650347530841827, -0.8385630249977112, 1.407746434211731, -0.3968145549297333, 1.5227645635604858, 0.02787056937813759, -0.4205769896507263, -1.857169270515442, 0.19621162116527557, 0.5419301986694336, -0.236742302775383, 0.7343138456344604, 0.02701488882303238, 0.6104968786239624, -1.104549765586853, -0.24068650603294373, 0.6518174409866333, 0.6168990731239319, -1.1853200197219849, -0.5069746375083923, 0.1875144988298416, 0.31637710332870483, 0.2308870404958725, -0.152983620762825, -1.376577615737915, -0.12398194521665573, -1.7274911403656006, 0.0553676038980484, 0.7065964937210083, -0.2714090645313263, -1.3525338172912598, 0.4523741602897644, 0.2877047657966614, 0.8726789355278015, -0.021803906187415123, -1.3934259414672852, 0.3106502294540405, -1.8704209327697754, 0.2009981870651245, 0.12338432669639587, -0.8415746092796326, -2.4619081020355225, 0.6237182021141052, 0.5943622589111328, -0.608020007610321, -2.0282952785491943, -0.8522984385490417, -1.1280208826065063, 1.877633810043335, 0.15573008358478546, -0.35549384355545044, 0.1165534108877182, 0.7098597884178162, 0.47633129358291626, -0.046409379690885544, 0.5908498764038086, -0.5342572927474976, 1.44736647605896, 0.4083510637283325, 0.6209722757339478, 1.027238130569458, 1.3726650476455688, -0.28296926617622375, -0.018917061388492584, 0.18425710499286652, -0.3258253335952759, -1.348402976989746, 0.5284386873245239, 0.0033300071954727173, 1.1287482976913452, 0.15240779519081116, -0.5348575115203857, -0.0004972172901034355, -0.3079269230365753, -0.2828940749168396, 0.5353473424911499, 1.2406201362609863, 1.7594480514526367, -0.04297139495611191, 0.9662273526191711, 0.071239173412323, 0.10443387925624847, 0.288479208946228, 0.3907362222671509, 0.14749500155448914, -0.5392590165138245, 0.1258363127708435, 0.8200002312660217, 0.025230364874005318, -0.9577836990356445, -0.19303475320339203, -0.5163901448249817, -0.5055752396583557, -0.21092312037944794, 1.1814336776733398, -0.11524821817874908, -0.40210896730422974, 0.9826206564903259, 1.5618298053741455, 0.8224124312400818, -1.8142434358596802, 1.1987357139587402, 0.08445961773395538, 0.5170271396636963, -0.9218463897705078, 1.6457465887069702, 1.0146502256393433, -1.4467984437942505, -0.8172034025192261, -0.12907393276691437, 0.3583180904388428, -0.6853911876678467, -0.6662577986717224, -0.6985197067260742, -0.719651460647583, -0.6773197054862976, -0.5589814782142639, -0.9323218464851379, 2.401747703552246, -5.184460163116455, -0.5017378330230713, -1.2865852117538452, 0.5738603472709656, -0.27340883016586304, 0.3473093509674072, -1.1187270879745483, -0.574564516544342, -0.16603663563728333, -1.681894063949585, 0.03101850301027298, 1.526999592781067, 0.4786497950553894, -0.3736502230167389, 0.3444042205810547, -0.12143673002719879, -0.7685807943344116, -1.31917142868042, 0.044598549604415894, 2.4957995414733887, 0.9126927852630615, -0.8415079116821289, -0.8103894591331482, 0.4755132496356964, 0.05915961414575577, 0.48853281140327454, 0.9529452323913574, 0.1997547149658203, 0.13972412049770355, -0.6796689629554749, -0.6185823678970337, 1.4881659746170044, 0.8647935390472412, 0.014031443744897842, -0.8500995635986328, -0.38715341687202454, 0.4430792033672333, 0.8855654001235962, 0.485082745552063, 0.9861289262771606, -0.8933203220367432, 0.6078487634658813, 0.9215259552001953, 0.4595985412597656, 0.9674554467201233, -1.5092369318008423, 0.6149734258651733, -0.1275792419910431, 1.0291765928268433, 1.8486708402633667, -1.5308375358581543, -0.08684782683849335, -0.11147090047597885, 0.1951395869255066, -1.18083918094635, 0.1391981542110443, 0.35027801990509033, 0.10211924463510513, -0.46763888001441956, -0.7702282071113586, -1.0020020008087158, 0.7275855541229248, 0.062096066772937775, -0.5133906006813049, -1.089035153388977, 0.47370216250419617, -0.6665972471237183, -0.8784930109977722, 1.453964352607727, 0.5271921157836914, 0.3903018534183502, -1.8466776609420776, 0.5633865594863892, -0.9151601791381836, 0.6935318112373352, -0.06773695349693298, -2.0234310626983643, -0.03893569856882095, -0.6373571157455444, 0.5474961400032043, -0.37796926498413086, -0.2155449092388153, 0.5353399515151978, -0.8103141188621521, 0.43922391533851624, -0.810628354549408, -0.3771328628063202, 0.4298626780509949, 1.364251971244812, -1.2353936433792114, 0.7979916930198669, 0.8555570244789124, 0.46776869893074036, 0.6815212965011597, -0.565815806388855, -0.09016931056976318, -0.31901419162750244, -0.5766921639442444, -0.47415411472320557, -1.6161112785339355, -0.06881754845380783, 0.1975868046283722, -0.5381942391395569, 0.8157709240913391, -1.0379638671875, 0.6637935638427734, -0.418308287858963, -0.4663133919239044, 0.12914496660232544, 0.031571246683597565, -2.072279214859009, -0.35369905829429626, 0.12634694576263428, 0.2607215940952301, 0.28745371103286743, -0.5631401538848877, 1.632615327835083, -0.7379958629608154, -0.7972100973129272, -1.2675458192825317, 0.9627929329872131, 0.41469606757164, 0.007001450750976801, -1.156762719154358, 0.8486863374710083, -0.17284809052944183, -0.35391294956207275, 1.4907259941101074, 0.29902663826942444, -1.958207368850708, 0.5889556407928467, 1.274540662765503, -0.30647802352905273, -1.4352281093597412, -0.21373698115348816, -1.4929436445236206, 0.03889666497707367, -0.19070234894752502, -1.1184064149856567, 1.0861709117889404, -1.4942899942398071, 0.23633615672588348, -1.8568570613861084, -0.9704742431640625, -0.2930331826210022, -0.3908209800720215, 0.32661667466163635, 1.4752060174942017, -0.7131973505020142, 1.3094205856323242, 0.8100525140762329, -0.8457136750221252, -0.344756543636322, -0.14296314120292664, -0.7993677854537964, -1.3493800163269043, 0.5909948348999023, -0.35481223464012146, -0.7926136255264282, -0.28622376918792725, -0.03065427765250206, -0.4132400155067444, 0.4077385365962982, 0.1145230382680893, 0.01499937754124403, 0.36452746391296387, -0.2813137471675873, 0.3120390474796295, -0.8260901570320129, 1.1091861724853516, 0.6391713619232178, -0.46771103143692017, -0.9073565006256104, -1.6671223640441895, -0.10504557192325592, 0.3686070740222931, -0.37446820735931396, 0.08992137014865875, -0.6551517248153687, -0.38230785727500916, -0.5373770594596863, 0.8772233724594116, -1.1435695886611938, 1.0195159912109375, 0.04320158064365387, 0.11802136152982712, -0.5158221125602722, -1.6886413097381592, -0.6209837794303894, -1.2414653301239014, -0.3701765239238739, 1.0896767377853394, -0.7374835014343262, -0.8543206453323364, -1.7532322406768799, 0.5304893851280212, 0.7586928009986877, 0.7525280714035034, 0.4829266667366028, 0.5750988125801086, 0.20755252242088318, -0.16236472129821777, -0.44000327587127686, -0.0946832001209259, -0.16477835178375244, -0.9315248131752014, 0.5444362759590149, -1.1343425512313843, 0.13148576021194458, -0.9887659549713135, 1.3079787492752075, -1.319437861442566, -0.4599985182285309, -0.8830530643463135, 0.13482657074928284, 1.299919843673706, 0.2723826467990875, 0.27738064527511597, 0.024554410949349403, -0.6497121453285217, 0.997928261756897, -0.29946017265319824, 1.036296010017395, 1.076870083808899, -1.6172351837158203, 1.496512770652771, 1.1841826438903809, 0.40636733174324036, -0.5938655734062195, 0.39680829644203186, -0.07258717715740204, 0.2972486913204193, 0.0437193438410759, -0.44954583048820496, 0.2953111231327057, 0.9295274019241333, 0.5160158276557922, -1.8039395809173584, -0.5138839483261108, -1.4925605058670044, 0.10443466901779175, -0.6801062226295471, -0.15071597695350647, 0.08446934819221497, -0.7515177726745605, -0.548183798789978, 0.2171030342578888, -0.6046884059906006, -0.49828702211380005, -0.5431618094444275, 0.07730695605278015, 1.3341387510299683, -0.5773117542266846, 1.1797008514404297, 1.1180176734924316, 0.9213765263557434, 0.4633031487464905, 0.41535094380378723, 0.647763192653656, -0.5383818745613098, -2.1602702140808105, 0.3850117027759552, -0.10052937269210815, -0.2715991735458374, -0.6809510588645935, -0.2853597402572632, -1.1600682735443115, -1.0267595052719116, -1.6507792472839355, 0.17247848212718964, -0.06558960676193237, -0.27286943793296814, -0.837938666343689, -0.29215118288993835, 0.45576733350753784, -0.8765187859535217, 0.7503643035888672, 0.7093344926834106, 1.6548750400543213, 0.5972182154655457]'))
FETCH APPROX FIRST 3 ROWS ONLY;






CREATE TABLE lab_vecstore_hysun2 (
    id VARCHAR2(50) DEFAULT SYS_GUID() PRIMARY KEY,
    dataset_name VARCHAR2(50) NOT NULL,
    document CLOB,
    cmetadata JSON,
    embedding VECTOR(*, FLOAT32)
);

insert into lab_vecstore_hysun2(dataset_name, document, cmetadata)
select dataset_name, document, cmetadata from lab_vecstore_hysun;
commit;


DBMS_VECTOR.LOAD_ONNX_MODEL(
model_name  IN  VARCHAR2,
model_data  IN  BLOB,
metadata    IN  JSON);


SQL> grant execute on DBMS_CLOUD to pocuser;
SQL> grant create mining model to pocuser;

-- https://docs.oracle.com/en/database/oracle/oracle-database/23/arpls/dbms_vector1.html#GUID-7F1D7992-D8F7-4AD9-9BF6-6EFFC1B0617A
DECLARE
    model_source BLOB := NULL;
BEGIN
    model_source := DBMS_CLOUD.get_object(
      object_uri      => 'https://objectstorage.ap-seoul-1.oraclecloud.com/n/sehubjapacprod/b/HysunPubBucket/o/bge-base-zh-v1.5.onnx'
    );

    DBMS_VECTOR.LOAD_ONNX_MODEL(
      model_name      => 'mydoc_model',
      model_data      => model_source,
      metadata        => JSON('{"function" : "embedding", "embeddingOutput" : "embedding"}')
    );
END;
/


select * from user_objects where object_type = 'MINING MODEL';

exec DBMS_VECTOR.DROP_ONNX_MODEL (model_name => 'HYSUN_BGE_ZH_MODEL', force => TRUE);


SELECT VECTOR_EMBEDDING(mydoc_model USING 'Hello, World' as input) AS embedding;

update lab_vecstore_hysun2 set embedding=VECTOR_EMBEDDING(mydoc_model USING document as input);
commit;


select document, 
  json_value(cmetadata, '$.source') as src_file
from lab_vecstore_hysun2
where dataset_name='oracledb_docs'
order by VECTOR_DISTANCE(embedding, VECTOR_EMBEDDING(mydoc_model USING 'Oracle 23ai 新特性' as input), COSINE) 
FETCH APPROX FIRST 3 ROWS ONLY;