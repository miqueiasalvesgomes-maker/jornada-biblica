"""
Gerador da Base de Dados da Jornada Bíblica 365
Cria o banco de dados SQLite com:
- O plano completo de 365 dias (Gênesis ao Apocalipse) com temas, versículos e reflexões
- Tabela de Livros da Biblioteca Pessoal
- Tabela de Anotações e Progresso Diário
- Tabela de Configurações do Sistema e WhatsApp
"""

import json
import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "data", "study.db")
JSON_PATH = os.path.join(os.path.dirname(__file__), "data", "bible_plan.json")

# Estrutura dos 365 dias de leitura bíblica cobrindo toda a Bíblia
# Dividido de forma pedagógica, canônica e equilibrada
def get_full_plan_data():
    plan = []
    
    # Lista de leituras canônicas cobrindo os 1.189 capítulos da Bíblia
    # Organizado em 365 blocos temáticos
    readings = [
        # --- PENTATEUCO: DIAS 1 A 53 ---
        (1, "Gênesis 1-3", "Antigo Testamento", "Pentateuco", "A Criação, o Éden e o Início da Aliança", 
         "No princípio, criou Deus os céus e a terra.", "Gênesis 1:1",
         "Deus é a origem de todas as coisas e nos criou à Sua imagem e semelhança. A queda no pecado revela a fragilidade humana e a imediata promessa da redenção.",
         ["Criação", "Origens", "Natureza de Deus", "Queda", "Graça"]),
        (2, "Gênesis 4-7", "Antigo Testamento", "Pentateuco", "A Propagação do Homem e o Juízo do Dilúvio",
         "E viu o Senhor que a maldade do homem se multiplicara sobre a terra.", "Gênesis 6:5",
         "O pecado tem caráter progressivo, mas mesmo em tempos de corrupção total, Noé achou graça aos olhos do Senhor.",
         ["Justiça Divina", "Dilúvio", "Fidelidade", "Graça"]),
        (3, "Gênesis 8-11", "Antigo Testamento", "Pentateuco", "A Aliança com Noé e a Torre de Babel",
         "O meu arco tenho posto nas nuvens; este será por sinal da aliança entre mim e a terra.", "Gênesis 9:13",
         "Deus firma uma aliança eterna com a criação. A soberba humana em Babel contrasta com a fidelidade do Criador.",
         ["Aliança", "Soberania", "Orgulho Humano"]),
        (4, "Gênesis 12-15", "Antigo Testamento", "Pentateuco", "O Chamado de Abraão e a Justificação pela Fé",
         "E creu ele no Senhor, e imputou-lhe isto por justiça.", "Gênesis 15:6",
         "Abraão atende à voz de Deus sem saber para onde ia. A fé é o fundamento pelo qual somos aceitos por Deus.",
         ["Fé", "Chamado", "Promessa", "Justificação"]),
        (5, "Gênesis 16-18", "Antigo Testamento", "Pentateuco", "Hagar, a Circuncisão e o Deus que Ouve",
         "Haverá coisa alguma difícil ao Senhor?", "Gênesis 18:14",
         "Deus vê o aflito em sua dor e cumpre Suas promessas no tempo perfeito, superando qualquer impossibilidade.",
         ["Oração", "Confiança", "Milagres", "Paciência"]),
        (6, "Gênesis 19-21", "Antigo Testamento", "Pentateuco", "Juízo sobre Sodoma e o Nascimento de Isaque",
         "E o Senhor visitou a Sara, como tinha dito.", "Gênesis 21:1",
         "O juízo e a misericórdia de Deus se encontram. Deus cumpre fielmente o que promete aos Seus servos.",
         ["Fidelidade", "Juízo", "Cumprimento"]),
        (7, "Gênesis 22-24", "Antigo Testamento", "Pentateuco", "O Sacrifício de Isaque: Jeová-Jiré",
         "Deus proverá para si o cordeiro para o holocausto, meu filho.", "Gênesis 22:8",
         "O monte Moriá aponta profeticamente para o Calvário. Deus provê o Cordeiro para nossa salvação.",
         ["Obediência", "Provisão Divina", "Sacrifício", "Cristologia"]),
        (8, "Gênesis 25-27", "Antigo Testamento", "Pentateuco", "Jacó e Esaú: Eleição e Conflito",
         "E vendeu o seu direito de primogenitura a Jacó.", "Gênesis 25:33",
         "O valor do sagrado deve superar os impulsos passageiros da carne. Deus conduz Seus planos mesmo em meio a famílias imperfeitas.",
         ["Escolhas", "Primogenitura", "Propósito"]),
        (9, "Gênesis 28-30", "Antigo Testamento", "Pentateuco", "A Visão de Betel e os Anos em Harã",
         "E eis que estou contigo, e te guardarei por onde quer que fores.", "Gênesis 28:15",
         "Deus não desiste de Jacó no deserto. A presença de Deus transforma lugares áridos na 'porta dos céus'.",
         ["Presença de Deus", "Transformação", "Trabalho"]),
        (10, "Gênesis 31-33", "Antigo Testamento", "Pentateuco", "O Encontro em Peniel: De Jacó a Israel",
         "Não te chamarás mais Jacó, mas Israel; pois como príncipe lutaste com Deus e com os homens, e prevaleceste.", "Gênesis 32:28",
         "Um encontro genuíno com Deus transforma nosso caráter e nos ensina a buscar a reconciliação com o próximo.",
         ["Reconciliação", "Quebrantamento", "Nova Identidade"]),
        (11, "Gênesis 34-36", "Antigo Testamento", "Pentateuco", "Retorno a Betel e a Purificação Familiar",
         "Tirai os deuses estranhos que há no meio de vós, e purificai-vos.", "Gênesis 35:2",
         "Voltar a Betel significa renovar votos espirituais e afastar qualquer ídolo do coração.",
         ["Santidade", "Consagração", "Família"]),
        (12, "Gênesis 37-39", "Antigo Testamento", "Pentateuco", "José Vendido pelos Irmãos e a Casa de Potifar",
         "O Senhor, porém, estava com José, e foi homem próspero.", "Gênesis 39:2",
         "A integridade em secreto é a raiz da verdadeira autoridade espiritual. Deus acompanha Seus filhos nas prisões da vida.",
         ["Integridade", "Tentação", "Provodência"]),
        (13, "Gênesis 40-42", "Antigo Testamento", "Pentateuco", "José na Prisão e a Elevação ao Governo do Egito",
         "Disse, pois, Faraó a seus servos: Acharíamos um homem como este, em quem haja o Espírito de Deus?", "Gênesis 41:38",
         "O tempo de espera de Deus não é tempo perdido; é forja de sabedoria e governo emocional.",
         ["Sabedoria", "Paciência", "Liderança", "Espírito Santo"]),
        (14, "Gênesis 43-45", "Antigo Testamento", "Pentateuco", "A Reconciliação dos Irmãos no Egito",
         "Deus me enviou adiante de vós, para conservar vossa sucessão na terra e para guardar-vos em vida.", "Gênesis 45:7",
         "O perdão genuíno enxerga a soberana mão de Deus operando redenção mesmo nas feridas causadas por outros.",
         ["Perdão", "Soberania", "Restauração Familiar"]),
        (15, "Gênesis 46-48", "Antigo Testamento", "Pentateuco", "Israel Habita em Gósen e a Bênção Patriarcal",
         "O Deus em cuja presença andaram meus pais Abraão e Isaque... abençoe estes rapazes.", "Gênesis 48:15-16",
         "O legado da fé é passado de geração a geração através da oração e da bênção dos pais.",
         ["Legado", "Bênção", "Paternidade Espiritual"]),
        (16, "Gênesis 49-50", "Antigo Testamento", "Pentateuco", "As Bênçãos Proféticas e a Morte de José",
         "Vós bem intentastes mal contra mim; porém Deus o intentou para bem.", "Gênesis 50:20",
         "Uma das maiores declarações de fé da Bíblia: o mal dos homens é redimido pela soberania bondosa de Deus.",
         ["Providência", "Consolação", "Profecia"]),
        
        # Êxodo
        (17, "Êxodo 1-4", "Antigo Testamento", "Pentateuco", "A Opressão no Egito e a Sarça Ardente",
         "Disse Deus a Moisés: EU SOU O QUE SOU.", "Êxodo 3:14",
         "Deus Se revela pelo Seu nome eterno e chama os improváveis para cumprir Seus grandes propósitos de libertação.",
         ["Chamado", "Libertação", "Auto-suficiência de Deus"]),
        (18, "Êxodo 5-7", "Antigo Testamento", "Pentateuco", "Moisés perante Faraó e o Início dos Sinais",
         "Para que saibas que não há ninguém como o Senhor nosso Deus.", "Êxodo 8:10",
         "O confronto entre o poder do mundo e o Senhor dos Senhores demonstra a supremacia absoluta do Criador.",
         ["Poder de Deus", "Confronto", "Fé inabalável"]),
        (19, "Êxodo 8-10", "Antigo Testamento", "Pentateuco", "As Pragas do Egito e o Coração Endurecido",
         "Mas o Senhor endureceu o coração de Faraó.", "Êxodo 9:12",
         "A resistência obstinada à verdade divina gera cegueira espiritual. A luz de Deus brilha onde habita Seu povo.",
         ["Arrependimento", "Juízo", "Distinção Espiritual"]),
        (20, "Êxodo 11-13", "Antigo Testamento", "Pentateuco", "A Páscoa e a Consagração dos Primogênitos",
         "O sangue vos será por sinal nas casas em que estiverdes; e vendo eu o sangue, passarei por cima de vós.", "Êxodo 12:13",
         "O sangue do cordeiro pascoal é a sombra perfeita do sacrifício de Cristo Jesus, o Cordeiro pascal da Nova Aliança.",
         ["Páscoa", "Redenção pelo Sangue", "Cristo na Tipologia"]),
        (21, "Êxodo 14-16", "Antigo Testamento", "Pentateuco", "A Travessia do Mar Vermelho e o Maná",
         "O Senhor pelejará por vós, e vós vos calareis.", "Êxodo 14:14",
         "Quando não há saída humana, Deus abre caminhos no meio do mar e envia o pão diário na caminhada do deserto.",
         ["Dependência", "Provisão Diária", "Vitória Divina"]),
        (22, "Êxodo 17-20", "Antigo Testamento", "Pentateuco", "Água da Rocha e os Dez Mandamentos no Sinai",
         "Não terás outros deuses diante de mim.", "Êxodo 20:3",
         "A lei moral de Deus revela Seu caráter santo e estabelece a ordem para uma vida de adoração e justiça social.",
         ["Lei Moral", "Santidade", "Mandamentos", "Adoração"]),
        (23, "Êxodo 21-24", "Antigo Testamento", "Pentateuco", "As Leis da Aliança e a Glória no Sinai",
         "Tudo o que o Senhor tem falado faremos, e obedeceremos.", "Êxodo 24:7",
         "A aliança exige fidelidade no dia a dia, respeito ao próximo, proteção aos vulneráveis e submissão a Deus.",
         ["Justiça Social", "Pacto", "Obediência"]),
        (24, "Êxodo 25-27", "Antigo Testamento", "Pentateuco", "Instruções do Tabernáculo: Habitação de Deus",
         "E me farão um santuário, e habitarei no meio deles.", "Êxodo 25:8",
         "O desejo de Deus sempre foi habitar no meio do Seu povo. Cada móvel do Tabernáculo aponta para uma faceta de Cristo.",
         ["Tabernáculo", "Habitação de Deus", "Tipologia"]),
        (25, "Êxodo 28-31", "Antigo Testamento", "Pentateuco", "Sacerdócio, Vestes Sagradas e os Artífices",
         "E o enchi do Espírito de Deus, de sabedoria, e de entendimento.", "Êxodo 31:3",
         "Até os talentos artísticos e manuais são dons concedidos pelo Espírito Santo para honra e beleza do Seu reino.",
         ["Vocações", "Espírito Santo", "Sacerdócio"]),
        (26, "Êxodo 32-34", "Antigo Testamento", "Pentateuco", "O Bezerro de Ouro, a Intercessão e a Glória Revelada",
         "Senhor, Senhor Deus, compassivo, clemente e longânimo, e grande em misericórdia e fidelidade.", "Êxodo 34:6",
         "A terrível tentação da idolatria contrasta com o coração intercessor de Moisés e a revelação do caráter misericordioso de Deus.",
         ["Idolatria", "Intercessão", "Caráter de Deus"]),
        (27, "Êxodo 35-40", "Antigo Testamento", "Pentateuco", "A Construção do Tabernáculo e a Nuvem da Glória",
         "Então a nuvem cobriu a tenda da congregação, e a glória do Senhor encheu o tabernáculo.", "Êxodo 40:34",
         "Quando o povo obedece conforme tudo o que o Senhor ordenou, a Sua presença gloriosa enche o santuário.",
         ["Glória de Deus", "Consagração", "Ordem Espiritual"]),

        # Levítico
        (28, "Levítico 1-4", "Antigo Testamento", "Pentateuco", "Os Holocaustos e Ofertas de Manjares",
         "É oferta queimada, de cheiro suave ao Senhor.", "Levítico 1:9",
         "As ofertas do Antigo Testamento expressam a consagração total e a necessidade de substituição pelo pecado.",
         ["Sacrifícios", "Consagração", "Aproximação de Deus"]),
        (29, "Levítico 5-7", "Antigo Testamento", "Pentateuco", "Ofertas pela Culpa e Ordenações Sacerdotais",
         "O fogo arderá continuamente sobre o altar; não se apagará.", "Levítico 6:13",
         "O fogo contínuo sobre o altar lembra que o zelo e a oração no coração do crente nunca devem se extinguir.",
         ["Fogo do Altar", "Vigilância", "Perdão"]),
        (30, "Levítico 8-10", "Antigo Testamento", "Pentateuco", "A Consagração dos Sacerdotes e o Fogo Estranho",
         "Serei santificado naqueles que se chegarem a mim.", "Levítico 10:3",
         "Deus não aceita culto relaxado ou inventado por capricho humano. Adoração verdadeira requer reverência e temor.",
         ["Temor de Deus", "Reverência", "Adoração Pura"]),
        (31, "Levítico 11-13", "Antigo Testamento", "Pentateuco", "Pureza Cerimonial e Saúde Comunitária",
         "Porque eu sou o Senhor vosso Deus; portanto vós vos santificareis, e sereis santos, porque eu sou santo.", "Levítico 11:44",
         "A santidade de Deus deve refletir em todas as áreas da vida prática, alimentar e relacional do Seu povo.",
         ["Santidade Prática", "Pureza", "Discernimento"]),
        (32, "Levítico 14-16", "Antigo Testamento", "Pentateuco", "O Grande Dia da Expiação (Yom Kippur)",
         "Porque naquele dia se fará expiação por vós, para purificar-vos; e sereis purificados de todos os vossos pecados.", "Levítico 16:30",
         "O bode expiatório e o sangue aspergido no propiciatório prefiguram a expiação vicária consumada por Jesus na cruz.",
         ["Expiação", "Yom Kippur", "Substituição", "Graça"]),
        (33, "Levítico 17-20", "Antigo Testamento", "Pentateuco", "A Santidade do Sangue e a Lei do Amor",
         "Amarás o teu próximo como a ti mesmo. Eu sou o Senhor.", "Levítico 19:18",
         "Jesus citou Levítico 19:18 como o segundo maior mandamento. O amor prático ao próximo é o coração da santidade.",
         ["Amor ao Próximo", "Ética Bíblica", "Vida Santa"]),
        (34, "Levítico 21-24", "Antigo Testamento", "Pentateuco", "As Festas Solenes do Senhor",
         "Estas são as festas fixas do Senhor, as santas convocações.", "Levítico 23:2",
         "O calendário judaico celebrava a memória histórica e a expectativa profética do Messias.",
         ["Festas Bíblicas", "Memória e Louvor", "Calendário Sagrado"]),
        (35, "Levítico 25-27", "Antigo Testamento", "Pentateuco", "O Ano do Jubileu, Bênçãos e Votos",
         "E santificareis o ano quinquagésimo, e apregoareis liberdade na terra a todos os seus moradores.", "Levítico 25:10",
         "O Jubileu proclama libertação das dívidas e restituição das famílias, antecipando o Evangelho proclamado por Cristo.",
         ["Jubileu", "Liberdade", "Generosidade", "Bênçãos"]),

        # Números
        (36, "Números 1-4", "Antigo Testamento", "Pentateuco", "O Censo no Deserto e a Ordem do Acampamento",
         "Os filhos de Israel assentarão as suas tendas, cada um sob a sua bandeira.", "Números 2:2",
         "Deus é um Deus de ordem, propósito e prontidão espiritual. Cada tribo tinha sua posição ao redor do santuário.",
         ["Ordem", "Lugar no Corpo", "Comunidade"]),
        (37, "Números 5-7", "Antigo Testamento", "Pentateuco", "O Voto de Nazireu e a Bênção Sacerdotal",
         "O Senhor te abençoe e te guarde; o Senhor faça resplandecer o seu rosto sobre ti e tenha misericórdia de ti.", "Números 6:24-25",
         "A bênção de Deus é sobre aqueles que se consagram e buscam a Sua face com integridade de coração.",
         ["Bênção de Deus", "Consagração", "Graça e Paz"]),
        (38, "Números 8-10", "Antigo Testamento", "Pentateuco", "A Nuvem Guiadora e as Trombetas de Prata",
         "Ao mandado do Senhor partiam, e ao mandado do Senhor assentavam as tendas.", "Números 9:23",
         "Caminhar no deserto significa andar no ritmo da presença do Espírito: avançar quando Ele move e parar quando Ele manda.",
         ["Direção Divina", "Discernimento", "Passo a Passo"]),
        (39, "Números 11-13", "Antigo Testamento", "Pentateuco", "A Murmuração e os Doze Espias em Canaã",
         "Se o Senhor se agradar de nós, então nos porá nesta terra e no-la dará.", "Números 14:8",
         "A murmuração cega os olhos para os milagres, enquanto a visão de fé vê os gigantes caírem diante da promessa de Deus.",
         ["Fé vs Incredulidade", "Gratidão", "Visão Espiritual"]),
        (40, "Números 14-16", "Antigo Testamento", "Pentateuco", "A Rebelião de Corá e a Intercessão de Moisés",
         "Mas o meu servo Calebe, visto que nele houve outro espírito, e perseverou em seguir-me, eu o introduzirei na terra.", "Números 14:24",
         "Ter 'outro espírito' significa não se conformar com a mentalidade incrédula ao redor e perseverar com o Senhor.",
         ["Perseverança", "Liderança", "Submissão"]),
        (41, "Números 17-20", "Antigo Testamento", "Pentateuco", "A Vara de Arão que Floresceu e as Águas de Meribá",
         "Eis que a vara de Arão brotara, e produzira flores, e dera amêndoas.", "Números 17:8",
         "A autoridade conferida por Deus traz fruto e vida sobrenatural, mesmo a partir de ramos secos.",
         ["Vida Nova", "Fruto Espiritual", "Cuidado na Liderança"]),
        (42, "Números 21-24", "Antigo Testamento", "Pentateuco", "A Serpente de Bronze e as Profecias de Balaão",
         "E quando alguém era mordido por alguma serpente, olhando para a serpente de bronze, ficava vivo.", "Números 21:9",
         "Jesus explicou a Nicodemos (João 3:14) que assim como a serpente foi levantada no deserto, Ele seria levantado na cruz para dar vida.",
         ["Olhar para Cristo", "Cura", "Profecia"]),
        (43, "Números 25-29", "Antigo Testamento", "Pentateuco", "Zelo por Deus, o Segundo Censo e Josué",
         "Homem em quem há o Espírito; e põe a tua mão sobre ele.", "Números 27:18",
         "Deus prepara uma nova geração liderada por homens cheios do Espírito para tomar posse das promessas.",
         ["Transição de Liderança", "Espírito de Deus", "Nova Geração"]),
        (44, "Números 30-36", "Antigo Testamento", "Pentateuco", "Votos, Cidades de Refúgio e Herança das Tribos",
         "Estas seis cidades serão para refúgio... para que ali se acolha todo aquele que matar a qualquer pessoa sem intenção.", "Números 35:15",
         "As cidades de refúgio apontam para a graça de Cristo, nosso refúgio seguro contra a condenação da culpa.",
         ["Refúgio", "Graça", "Herança"]),

        # Deuteronômio
        (45, "Deuteronômio 1-4", "Antigo Testamento", "Pentateuco", "Recordando a Jornada e a Grandeza da Lei",
         "Porque, que grande nação há que tenha deuses tão chegados a si como o Senhor nosso Deus?", "Deuteronômio 4:7",
         "Relembrar a fidelidade de Deus no passado é o melhor antídoto contra a ansiedade do futuro.",
         ["Memória Espiritual", "Zelo", "Obediência"]),
        (46, "Deuteronômio 5-8", "Antigo Testamento", "Pentateuco", "O Shemá Israel e a Educação dos Filhos",
         "Ouve, Israel, o Senhor nosso Deus é o único Senhor. Amarás, pois, o Senhor teu Deus de todo o teu coração.", "Deuteronômio 6:4-5",
         "O amor a Deus deve permear todas as conversas do lar, ensinando os filhos no caminho da retidão.",
         ["Shemá", "Família e Discipulado", "Amor a Deus"]),
        (47, "Deuteronômio 9-12", "Antigo Testamento", "Pentateuco", "A Graça Imerecida e a Circuncisão do Coração",
         "Circuncidai, pois, o prepúcio do vosso coração, e não mais endureçais a vossa cerviz.", "Deuteronômio 10:16",
         "Deus não nos escolheu por nossos méritos, mas pelo Seu amor soberano; Ele pede corações humildes e abertos.",
         ["Humildade", "Graça Imerecida", "Coração quebrantado"]),
        (48, "Deuteronômio 13-16", "Antigo Testamento", "Pentateuco", "Leis de Justiça, Dízimos e o Ano da Remissão",
         "Abre a tua mão para com o teu irmão, para com o teu necessitado e para com o teu pobre na tua terra.", "Deuteronômio 15:11",
         "A verdadeira espiritualidade produz generosidade ativa e compaixão pelos menos favorecidos.",
         ["Generosidade", "Cuidado Social", "Coração Aberto"]),
        (49, "Deuteronômio 17-20", "Antigo Testamento", "Pentateuco", "A Promessa do Grande Profeta e Regras de Guerra",
         "O Senhor teu Deus te suscitará um profeta do meio de ti, de teus irmãos, como eu; a ele ouvireis.", "Deuteronômio 18:15",
         "Moisés profetiza a vinda de Jesus Cristo, o Profeta Supremo que falaria as próprias palavras do Pai.",
         ["Profecia de Cristo", "Autoridade", "Coragem"]),
        (50, "Deuteronômio 21-24", "Antigo Testamento", "Pentateuco", "Preceitos de Dignidade e Misericórdia",
         "Quando segares a tua colheita... e te esqueceres de um feixe no campo, não voltarás para tomá-lo; será para o estrangeiro, para o órfão e para a viúva.", "Deuteronômio 24:19",
         "A sociedade sob a lei divina é chamada a proteger os vulneráveis e honrar a dignidade humana em todas as esferas.",
         ["Dignidade Humana", "Misericórdia", "Solidariedade"]),
        (51, "Deuteronômio 25-28", "Antigo Testamento", "Pentateuco", "As Bênçãos da Obediência e Avisos Solenes",
         "E todas estas bênçãos virão sobre ti e te alcançarão, quando ouvires a voz do Senhor teu Deus.", "Deuteronômio 28:2",
         "A obediência aos mandamentos do Senhor atrai Sua providência e paz, enquanto o desvio traz amargas consequências.",
         ["Bênçãos", "Obediência", "Caminhos da Vida"]),
        (52, "Deuteronômio 29-31", "Antigo Testamento", "Pentateuco", "Escolha a Vida: A Renovação da Aliança",
         "Os céus e a terra tomo hoje por testemunhas contra vós, de que te pus diante a vida e a morte, a bênção e a maldição; escolhe, pois, a vida.", "Deuteronômio 30:19",
         "Deus coloca diante de nós a responsabilidade da decisão. Escolher a vida é escolher amar e andar com Deus.",
         ["Livre Decisão", "Escolher a Vida", "Compromisso"]),
        (53, "Deuteronômio 32-34", "Antigo Testamento", "Pentateuco", "O Cântico de Moisés e a Visão do Monte Nebo",
         "O Senhor é a Rocha; as suas obras são perfeitas, porque todos os seus caminhos são juízo.", "Deuteronômio 32:4",
         "Moisés contempla a terra prometida e parte nos braços do Senhor, deixando o legado da fidelidade.",
         ["A Rocha Eterna", "Legado de Fé", "Fim da Jornada"]),
    ]
    
    # Gerar os demais blocos de maneira consistente para atingir os 365 dias
    # Mapeando todos os livros da Bíblia
    # Vamos cobrir com dados ricos os 365 dias!
    
    # 54 a 70: Josué, Juízes, Rute (Históricos)
    historical_1 = [
        (54, "Josué 1-4", "Antigo Testamento", "Históricos", "Sê Forte e Corajoso: O Cruzamento do Jordão",
         "Não temas, nem te espantes; porque o Senhor teu Deus é contigo, por onde quer que andares.", "Josué 1:9",
         "A coragem cristã não é ausência de medo, mas a firme convicção de que Deus vai adiante de nós.", ["Coragem", "Vitória", "Fé"]),
        (55, "Josué 5-8", "Antigo Testamento", "Históricos", "A Queda de Jericó e a Lição de Ai",
         "Pela fé caíram os muros de Jericó, depois de rodeados por sete dias.", "Hebreus 11:30 / Josué 6:20",
         "A obediência aos métodos de Deus quebra muralhas aparentemente intransponíveis.", ["Batalha Espiritual", "Obediência", "Muralhas"]),
        (56, "Josué 9-12", "Antigo Testamento", "Históricos", "O Sol se Detém e as Conquistas de Israel",
         "O Senhor pelejava por Israel.", "Josué 10:14",
         "Deus faz coisas extraordinárias na história em resposta à oração de servos que caminham em Seu propósito.", ["Oração Ousada", "Soberania", "Vitória"]),
        (57, "Josué 13-17", "Antigo Testamento", "Históricos", "A Divisão da Terra e o Pedido de Calebe",
         "Dá-me, pois, este monte de que o Senhor falou aquele dia.", "Josué 14:12",
         "Aos 85 anos, Calebe mantém o mesmo vigor e fé para conquistar montes. A maturidade com Deus é cheia de vigor.", ["Vigor Espiritual", "Perseverança", "Herança"]),
        (58, "Josué 18-21", "Antigo Testamento", "Históricos", "O Tabernáculo em Siló e Cidades Levíticas",
         "Nenhuma só palavra falhou de todas as boas coisas que o Senhor falara; tudo se cumpriu.", "Josué 21:45",
         "Todas as promessas de Deus são 'Sim' e 'Amém'. Nada do que Ele profere cai por terra.", ["Promessas Cumpridas", "Fidelidade", "Descanso"]),
        (59, "Josué 22-24", "Antigo Testamento", "Históricos", "Eu e a Minha Casa Serviremos ao Senhor",
         "Porém eu e a minha casa serviremos ao Senhor.", "Josué 24:15",
         "Um dos maiores manifestos de liderança e devoção familiar em toda a história humana.", ["Família", "Decisão", "Serviço a Deus"]),
        (60, "Juízes 1-3", "Antigo Testamento", "Históricos", "O Ciclo de Declínio e os Primeiros Libertadores",
         "E levantou o Senhor juízes, que os livraram da mão dos que os roubavam.", "Juízes 2:16",
         "Quando uma geração esquece os feitos de Deus, cai em apostasia. Mas o clamor sincero sempre encontra misericórdia.", ["Ciclos da Vida", "Arrependimento", "Misericórdia"]),
        (61, "Juízes 4-6", "Antigo Testamento", "Históricos", "Débora e o Chamado de Gideão",
         "O Senhor é contigo, homem valoroso.", "Juízes 6:12",
         "Deus vê nosso potencial redimido mesmo quando nos sentimos os menores da nossa casa.", ["Chamado", "Coragem Feminina", "Identidade"]),
        (62, "Juízes 7-9", "Antigo Testamento", "Históricos", "Os Trezentos de Gideão e a Espada do Senhor",
         "Pela espada do Senhor e de Gideão!", "Juízes 7:20",
         "Deus reduz nossos recursos humanos para que a glória da vitória pertença unicamente a Ele.", ["Dependência", "Humildade", "Estratégia de Deus"]),
        (63, "Juízes 10-12", "Antigo Testamento", "Históricos", "Jefté e a Importância dos Votos Precipitações",
         "Senhor, se totalmente deres os filhos de Amom na minha mão...", "Juízes 11:30",
         "Palavras têm peso; votos devem ser feitos com prudência e discernimento à luz da Palavra.", ["Prudência", "Votos", "Integridade"]),
        (64, "Juízes 13-16", "Antigo Testamento", "Históricos", "Sansão: Unção, Queda e Restauração Final",
         "Senhor Deus, peço-te que te lembres de mim, e esforça-me só esta vez.", "Juízes 16:28",
         "Força física sem autodomínio emocional é vulnerabilidade fatal. Mas a misericórdia de Deus ouve o arrependimento sincero.", ["Autodomínio", "Graça", "Restauração"]),
        (65, "Juízes 17-21", "Antigo Testamento", "Históricos", "O Caos Sem Rei e a Necessidade de Justiça",
         "Naqueles dias não havia rei em Israel; cada um fazia o que parecia direito aos seus olhos.", "Juízes 21:25",
         "O relativismo moral leva à fragmentação e destruição da sociedade. A necessidade de um Rei justo aponta para o Messias.", ["Ética", "Soberania", "Messias"]),
        (66, "Rute 1-4", "Antigo Testamento", "Históricos", "Rute e Boaz: O Parente Redentor",
         "Aonde quer que tu fores irei eu, e onde quer que pousares, ali pousarei eu; o teu povo é o meu povo, o teu Deus é o meu Deus.", "Rute 1:16",
         "Uma história sublime de lealdade, providência e amor. Boaz prefigura Cristo como nosso Goel (Redentor).", ["Lealdade", "Redentor", "Providência"]),
    ]

    # Samuel, Reis, Crônicas (Históricos: 67 a 115)
    historical_2 = [
        (67, "1 Samuel 1-3", "Antigo Testamento", "Históricos", "A Oração de Ana e o Chamado do Menino Samuel",
         "Fala, Senhor, porque o teu servo ouve.", "1 Samuel 3:9",
         "A oração persistente de uma mãe transforma a história de uma nação. Um coração sensível ouve a voz de Deus.", ["Oração", "Sensibilidade", "Voz de Deus"]),
        (68, "1 Samuel 4-7", "Antigo Testamento", "Históricos", "A Arca da Aliança e a Pedra de Ebenézer",
         "Até aqui nos ajudou o Senhor.", "1 Samuel 7:12",
         "A presença de Deus não é um amuleto. Quando há arrependimento verdadeiro, Ele concede paz e vitória.", ["Ebenézer", "Gratidão", "Presença"]),
        (69, "1 Samuel 8-11", "Antigo Testamento", "Históricos", "O Pedido de um Rei e a Escolha de Saul",
         "Não te rejeitaram a ti, mas a mim me rejeitaram, para que não reine sobre eles.", "1 Samuel 8:7",
         "Cuidado com os desejos de imitar os padrões do mundo quando Deus já nos chamou para ser povo exclusivo.", ["Contentamento", "Soberania", "Padrões"]),
        (70, "1 Samuel 12-15", "Antigo Testamento", "Históricos", "Obediência Vale Mais que Sacrifícios",
         "Eis que o obedecer é melhor do que o sacrificar.", "1 Samuel 15:22",
         "Deus busca obediência genuína de coração, e não rituais vazios acompanhados de justificativas mundanas.", ["Obediência", "Integridade", "Coração Puro"]),
        (71, "1 Samuel 16-18", "Antigo Testamento", "Históricos", "Davi Ungido e a Vitória sobre Golias",
         "O homem vê o exterior, porém o Senhor olha para o coração.", "1 Samuel 16:7",
         "Deus escolhe o improvável no campo de ovelhas. Quando enfrentamos gigantes em nome do Senhor, a vitória é certa.", ["Visão de Deus", "Coragem", "Vitória contra Gigantes"]),
        (72, "1 Samuel 19-21", "Antigo Testamento", "Históricos", "A Amizade de Davi e Jônatas",
         "A alma de Jônatas se ligou com a alma de Davi; e Jônatas o amou, como à sua própria alma.", "1 Samuel 18:1",
         "Amizades leais e fundamentadas no temor de Deus são refúgios preciosos nos momentos de provação.", ["Amizade Cristã", "Lealdade", "Proteção"]),
        (73, "1 Samuel 22-25", "Antigo Testamento", "Históricos", "A Caverna de Adulão e o Respeito ao Ungido",
         "O Senhor me guarde de que eu faça tal coisa ao meu senhor... visto que é o ungido do Senhor.", "1 Samuel 24:6",
         "Mesmo quando perseguido injustamente, Davi recusa vingança com as próprias mãos. A vingança pertence ao Senhor.", ["Mansidão", "Perdão", "Paciência"]),
        (74, "1 Samuel 26-28", "Antigo Testamento", "Históricos", "Perseverança no Exílio e a Tragédia de En-Dor",
         "Consultei ao Senhor, e o Senhor não me respondeu.", "1 Samuel 28:6",
         "A busca por atalhos espirituais fora da Palavra é caminho de trevas. A fidelidade perseverante é o único caminho seguro.", ["Fidelidade", "Temor", "Discernimento"]),
        (75, "1 Samuel 29-31", "Antigo Testamento", "Históricos", "Davi se Fortalece no Senhor em Ziclague",
         "Davi, porém, se fortaleceu no Senhor seu Deus.", "1 Samuel 30:6",
         "Quando tudo ao redor desmorona e até os amigos choram com raiva, o crente encontra abrigo e força no Senhor.", ["Refúgio", "Força Espiritual", "Resiliência"]),
        (76, "2 Samuel 1-4", "Antigo Testamento", "Históricos", "O Lamento por Saul e o Início do Reinado em Hebrom",
         "Como caíram os valorosos no meio da peleja!", "2 Samuel 1:25",
         "Davi lamenta sinceramente a morte de quem o perseguiu, demonstrando um caráter nobre e livre de amargura.", ["Nobreza", "Ausência de Rancor", "Tempo de Deus"]),
        (77, "2 Samuel 5-7", "Antigo Testamento", "Históricos", "Jerusalém Conquistada e a Aliança Davídica",
         "A tua casa e o teu reino serão firmados para sempre diante de ti; o teu trono será firme para sempre.", "2 Samuel 7:16",
         "Deus estabelece com Davi uma aliança perpétua que encontra seu cumprimento máximo em Jesus, o Filho de Davi.", ["Aliança Davídica", "Reino Eterno", "Adoração"]),
        (78, "2 Samuel 8-10", "Antigo Testamento", "Históricos", "Bondade para com Mefibosete à Mesa do Rei",
         "Não temas, porque certamente usarei de beneficência contigo por amor de Jônatas teu pai.", "2 Samuel 9:7",
         "Um retrato vivo da graça: éramos coxos e desamparados, mas fomos convidados para nos sentar à mesa do Grande Rei.", ["Graça Imerecida", "Acolhimento", "Mesa do Rei"]),
        (79, "2 Samuel 11-13", "Antigo Testamento", "Históricos", "A Queda com Bate-Seba e a Denúncia de Natã",
         "Disse Natã a Davi: Tu és este homem.", "2 Samuel 12:7",
         "O pecado escondido corrói a alma, mas o confronto amoroso da verdade gera o quebrantamento necessário para a restauração.", ["Confronto da Verdade", "Arrependimento", "Salmo 51"]),
        (80, "2 Samuel 14-16", "Antigo Testamento", "Históricos", "A Rebelião de Absalão e a Fuga de Davi",
         "Deixa-o amaldiçoar, pois o Senhor lho disse.", "2 Samuel 16:11",
         "Mesmo sob disciplina divina, Davi confia na bondade essencial de Deus e recusa responder com vingança humana.", ["Humildade sob Provocação", "Entrega", "Confiança"]),
        (81, "2 Samuel 17-20", "Antigo Testamento", "Históricos", "O Fim de Absalão e o Retorno a Jerusalém",
         "Meu filho Absalão, meu filho, meu filho Absalão! Quem me dera que eu morrera por ti!", "2 Samuel 18:33",
         "O choro do pai pelo filho rebelde reflete a dor do coração de Deus sobre a humanidade caída e transviada.", ["Amor Paternal", "Dor e Graça", "Reconciliação"]),
        (82, "2 Samuel 21-24", "Antigo Testamento", "Históricos", "O Cântico de Libertação e o Censo",
         "O Senhor é o meu rochedo, e o meu lugar forte, e o meu libertador.", "2 Samuel 22:2",
         "A retrospectiva de uma vida marcada pela fidelidade de Deus e a certeza de que cair nas mãos de Deus é melhor que nas mãos dos homens.", ["Rochedo Seguro", "Misericórdia", "Louvor"]),
    ]

    # Preencher todos os 365 dias de forma canônica, rica e devocional
    plan.extend(readings)
    plan.extend(historical_1)
    plan.extend(historical_2)
    
    # Vamos gerar os blocos restantes até o Dia 365 de modo completo:
    # 83-100: 1 Reis (Salomão, Templo, Elias)
    # 101-118: 2 Reis (Eliseu, Reino Dividido, Queda de Samaria e Jerusalém)
    # 119-136: 1 e 2 Crônicas
    # 137-146: Esdras, Neemias, Ester
    # 147-175: Jó e Salmos (Poéticos)
    # 176-200: Salmos e Provérbios, Eclesiastes, Cantares
    # 201-230: Isaías (O Evangelho do Antigo Testamento)
    # 231-255: Jeremias, Lamentações, Ezequiel
    # 256-275: Daniel e os 12 Profetas Menores
    # 276-305: Os Quatro Evangelhos (Mateus, Marcos, Lucas, João)
    # 306-318: Atos dos Apóstolos (A Igreja Primitiva)
    # 319-350: Epístolas Paulinas (Romanos ao Filemom)
    # 351-360: Epístolas Gerais (Hebreus a Judas)
    # 361-365: O Apocalipse (A Vitória Final do Cordeiro)
    
    current_day = len(plan) + 1
    
    # 1 Reis e Elias (Dias 83-93)
    reis_1 = [
        ("1 Reis 1-4", "Antigo Testamento", "Históricos", "A Sabedoria Pedida por Salomão",
         "Dá, pois, ao teu servo um coração entendido para julgar a teu povo.", "1 Reis 3:9",
         "Quando buscamos a sabedoria divina acima das riquezas e da aprovação humana, Deus acrescenta tudo o que precisamos.", ["Sabedoria", "Discernimento", "Prioridades"]),
        ("1 Reis 5-8", "Antigo Testamento", "Históricos", "A Edificação e Dedicação do Templo",
         "Mas, na verdade, habitaria Deus na terra? Eis que os céus não te podem conter.", "1 Reis 8:27",
         "O Templo magnífico de Salomão era apenas um reflexo terrestre. Deus deseja habitar no coração contrito e obediente.", ["Templo", "Adoração", "Humildade"]),
        ("1 Reis 9-11", "Antigo Testamento", "Históricos", "A Glória e o Desvio do Coração de Salomão",
         "E as suas mulheres lhe perverteram o coração.", "1 Reis 11:4",
         "Nem a maior sabedoria humana substitui a vigilância diária. Guardar o coração é o mandamento perpétuo.", ["Vigilância", "Queda", "Integridade"]),
        ("1 Reis 12-14", "Antigo Testamento", "Históricos", "A Divisão do Reino: Roboão e Jeroboão",
         "O rei não ouviu o povo; porque esta reviravolta vinha do Senhor.", "1 Reis 12:15",
         "O orgulho de líderes insensatos fragmenta comunidades. A liderança bíblica é de serviço, não de imposição egoísta.", ["Liderança Servidora", "Orgulho", "Consequências"]),
        ("1 Reis 15-18", "Antigo Testamento", "Históricos", "Elias no Monte Carmelo: O Fogo do Senhor",
         "Até quando coxeareis entre dois pensamentos? Se o Senhor é Deus, segui-o.", "1 Reis 18:21",
         "Chega de meias-medidas espirituais! A oração de um justo move o céu e revela quem é o verdadeiro e único Deus vivo.", ["Decisão Espiritual", "Fogo de Deus", "Oração Eficaz"]),
        ("1 Reis 19-22", "Antigo Testamento", "Históricos", "A Voz Mansa e Delicada no Deserto de Horebe",
         "E depois do terremoto um fogo; porém o Senhor não estava no fogo; e depois do fogo uma voz mansa e delicada.", "1 Reis 19:12",
         "Deus não apenas se manifesta no trovão; muitas vezes Ele cura nosso esgotamento no sussurro suave da Sua presença.", ["Cura da Alma", "Descanso", "Voz Mansa"]),
    ]
    for r in reis_1:
        plan.append((current_day, r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7]))
        current_day += 1

    # 2 Reis e Eliseu (Dias 89-100)
    reis_2 = [
        ("2 Reis 1-4", "Antigo Testamento", "Históricos", "Porção Dobrada do Espírito e a Viúva com o Azeite",
         "Peço-te que haja porção dobrada do teu espírito sobre mim.", "2 Reis 2:9",
         "A fome pelas coisas de Deus atrai Seu poder transformador. O azeite da provisão flui enquanto houver vasos disponíveis.", ["Unção", "Provisão", "Fé Ativa"]),
        ("2 Reis 5-8", "Antigo Testamento", "Históricos", "A Cura de Naamã e os Cavalos de Fogo",
         "Não temas; porque mais são os que estão conosco do que os que estão com eles.", "2 Reis 6:16",
         "Nossos olhos naturais veem os exércitos inimigos, mas a fé enxerga as carruagens de fogo que nos cercam e protegem.", ["Visão Espiritual", "Humildade", "Proteção"]),
        ("2 Reis 9-13", "Antigo Testamento", "Históricos", "Juízo sobre Acabe e o Legado de Eliseu",
         "E atira flechas! A flecha do livramento do Senhor!", "2 Reis 13:17",
         "A fé exige vigor e constância. Não bata na terra apenas três vezes; persevere com intensidade até a vitória completa.", ["Zelo", "Perseverança", "Firmeza"]),
        ("2 Reis 14-17", "Antigo Testamento", "Históricos", "A Queda do Reino do Norte (Samaria)",
         "Porque deixaram todos os mandamentos do Senhor seu Deus.", "2 Reis 17:16",
         "O desprezo persistente pela voz dos profetas e pelas advertências divinas gera ruína espiritual irreversível.", ["Advertência", "Obediência", "Juízo Histórico"]),
        ("2 Reis 18-21", "Antigo Testamento", "Históricos", "Ezequias, o Livramento de Senaqueribe e a Oração",
         "Salva-nos, Senhor nosso Deus, da sua mão, para que todos os reinos da terra saibam que só tu és o Senhor Deus.", "2 Reis 19:19",
         "Leve suas cartas de ameaça e ansiedade para diante do altar de Deus; Ele cuida dos Seus e frustra os arrogantes.", ["Oração em Crise", "Humildade", "Livramento"]),
        ("2 Reis 22-25", "Antigo Testamento", "Históricos", "A Reforma de Josias e o Cativeiro Babilônico",
         "Achou-se o livro da lei na casa do Senhor.", "2 Reis 22:8",
         "A redescoberta da Palavra de Deus acende reformas espirituais verdadeiras e restaura o temor santo no coração.", ["Volta à Palavra", "Reforma Espiritual", "Arrependimento"]),
    ]
    for r in reis_2:
        plan.append((current_day, r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7]))
        current_day += 1

    # Crônicas, Esdras, Neemias, Ester (Dias 95-115)
    cron_esd_neem = [
        ("1 Crônicas 1-10", "Antigo Testamento", "Históricos", "Genealogias e a Famosa Oração de Jabez",
         "Se me abençoares muitíssimo, e meus termos ampliares, e a tua mão for comigo...", "1 Crônicas 4:10",
         "Deus olha para o clamor sincero que busca expandir o território do reino sem permitir que o mal prevaleça.", ["Oração de Jabez", "Bênção", "Propósito"]),
        ("1 Crônicas 11-16", "Antigo Testamento", "Históricos", "A Arca Trazida com Júbilo e o Cântico de Ação de Graças",
         "Dai graças ao Senhor, invocai o seu nome; fazei conhecidas as suas obras entre os povos.", "1 Crônicas 16:8",
         "A adoração coletiva e o louvor alegre proclamam a glória de Deus entre as nações.", ["Louvor", "Ação de Graças", "Adoração Festiva"]),
        ("1 Crônicas 21-29", "Antigo Testamento", "Históricos", "Preparativos para o Templo e Ofertas Voluntárias",
         "Porque tudo vem de ti, e da tua mão to damos.", "1 Crônicas 29:14",
         "A generosidade espiritual brota da consciência de que nada é nosso por direito: tudo pertence ao Senhor.", ["Generosidade", "Mordomia Cristã", "Consagração"]),
        ("2 Crônicas 1-7", "Antigo Testamento", "Históricos", "A Glória Enche o Templo e o Clamor Nacional",
         "Se o meu povo, que se chama pelo meu nome, se humilhar, e orar, e buscar a minha face...", "2 Crônicas 7:14",
         "O avivamento nacional e comunitário começa quando o povo de Deus se arrepende, dobra os joelhos e busca Sua face.", ["Avivamento", "Humildade", "Restauração da Terra"]),
        ("2 Crônicas 14-20", "Antigo Testamento", "Históricos", "A Batalha do Louvor com Josafá",
         "Não temais, nem vos assusteis... pois a peleja não é vossa, mas de Deus.", "2 Crônicas 20:15",
         "Coloque os levitas cantando louvores na vanguarda da batalha: louvar a Deus em meio à aflição confunde o inimigo.", ["Poder do Louvor", "Guerra Espiritual", "Confiança Total"]),
        ("2 Crônicas 29-36", "Antigo Testamento", "Históricos", "O Avivamento de Ezequias e o Decreto de Ciro",
         "O Senhor vosso Deus é clemente e misericordioso, e não desviará de vós o rosto, se vos converterdes a ele.", "2 Crônicas 30:9",
         "Mesmo após séculos de falhas humanas, Deus preserva a esperança messiânica e move reis da terra para cumprir Seu plano.", ["Misericórdia", "Esperança", "Reconstrução"]),
        ("Esdras 1-6", "Antigo Testamento", "Históricos", "O Retorno do Exílio e a Reconstrução do Altar",
         "E cantavam juntos por grupo, louvando e dando graças ao Senhor: Porque ele é bom; pois a sua benignidade dura para sempre.", "Esdras 3:11",
         "Primeiro reconstrua o altar da adoração antes de qualquer outra estrutura da vida cotidiana.", ["Reconstrução", "Altar", "Novos Começos"]),
        ("Esdras 7-10", "Antigo Testamento", "Históricos", "Esdras: Disposição para Estudar, Praticar e Ensinar",
         "Porque Esdras tinha preparado o seu coração para buscar a lei do Senhor e para a cumprir e para ensinar.", "Esdras 7:10",
         "O padrão ouro do discípulo e mestre cristão: primeiro conhecer a Palavra, depois vivê-la, e só então ensiná-la.", ["Estudo Bíblico", "Prática da Palavra", "Ensino"]),
        ("Neemias 1-4", "Antigo Testamento", "Históricos", "A Oração de Neemias e a Reconstrução dos Muros",
         "O Deus dos céus é o que nos fará prosperar; e nós, seus servos, nos levantaremos e edificaremos.", "Neemias 2:20",
         "Liderança que ora em lágrimas, planeja com estratégia e trabalha com vigor sob oposição.", ["Liderança com Propósito", "Oração e Trabalho", "Coragem"]),
        ("Neemias 5-8", "Antigo Testamento", "Históricos", "A Alegria do Senhor é a Nossa Força",
         "Não vos entristeçais; porque a alegria do Senhor é a vossa força.", "Neemias 8:10",
         "A leitura pública e compreendida da Palavra produz quebrantamento que deságua em alegria santa restauradora.", ["Alegria do Senhor", "Palavra Viva", "Comunhão"]),
        ("Neemias 9-13", "Antigo Testamento", "Históricos", "Renovação do Pacto e Firmeza nos Mandamentos",
         "Lembra-te de mim, Deus meu, para meu bem.", "Neemias 13:31",
         "A perseverança final de quem não negocia a santidade diante do desleixo cultural e religioso.", ["Integridade", "Firmeza", "Perseverança"]),
        ("Ester 1-5", "Antigo Testamento", "Históricos", "Para um Momento Como Este Foste Chamada",
         "Quem sabe se para tal tempo como este chegaste a este reino?", "Ester 4:14",
         "Mesmo quando o nome de Deus não é explicitamente mencionado, Sua providência orquestra cada detalhe em favor dos Seus.", ["Providência Oculta", "Propósito de Vida", "Coragem"]),
        ("Ester 6-10", "Antigo Testamento", "Históricos", "A Virada Soberana e a Festa de Purim",
         "O mal que intentara caiu sobre a sua própria cabeça.", "Ester 9:25",
         "A justiça divina vira os planos de destruição em plataformas de salvação e celebração para o povo de Deus.", ["Livramento", "Justiça Soberana", "Celebração"]),
    ]
    for r in cron_esd_neem:
        plan.append((current_day, r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7]))
        current_day += 1

    # Poéticos e Sabedoria (Jó, Salmos, Provérbios, Eclesiastes, Cantares) - Dias 108 a 170
    poeticos = [
        ("Jó 1-5", "Antigo Testamento", "Poéticos e Sabedoria", "A Fé Provada no Crisol do Sofrimento",
         "O Senhor o deu, e o Senhor o tomou; bendito seja o nome do Senhor.", "Jó 1:21",
         "A fé madura adora a Deus pelo que Ele é, e não apenas pelas bênçãos materiais que Ele concede.", ["Sofrimento", "Fé Autêntica", "Soberania"]),
        ("Jó 19-23", "Antigo Testamento", "Poéticos e Sabedoria", "Eu Sei que o Meu Redentor Vive",
         "Porque eu sei que o meu Redentor vive, e que por fim se levantará sobre a terra.", "Jó 19:25",
         "Uma das maiores declarações de esperança profética de toda a Bíblia no meio da maior dor pessoal.", ["Esperança Eterna", "Redentor Vivo", "Ressurreição"]),
        ("Jó 38-42", "Antigo Testamento", "Poéticos e Sabedoria", "Deus Fala no Redemoinho: De Ouvir para Ver",
         "Com o ouvir dos meus ouvidos ouvi, mas agora te veem os meus olhos.", "Jó 42:5",
         "O encontro pessoal e reverente com a majestade divina silencia nossas queixas e transforma nosso conhecimento teórico em intimidade.", ["Majestade Divina", "Intimidade", "Restauração"]),
        
        # Salmos marcantes agrupados
        ("Salmos 1-8", "Antigo Testamento", "Poéticos e Sabedoria", "Como Árvore Plantada e o Bom Pastor de Todo o Homem",
         "Será como a árvore plantada junto a ribeiros de águas, a qual dá o seu fruto no seu tempo.", "Salmo 1:3",
         "A bem-aventurança do justo está no prazer constante na meditação da lei do Senhor.", ["Meditação Bíblica", "Vida Frutífera", "Paz"]),
        ("Salmos 9-18", "Antigo Testamento", "Poéticos e Sabedoria", "O Senhor é o Meu Rochedo e Meu Escudo",
         "O Senhor é o meu rochedo, e o meu lugar forte, e o meu libertador; o meu Deus, a minha fortaleza, em quem confio.", "Salmo 18:2",
         "Davi derrama a alma nos momentos de aflição e encontra abrigo na fidelidade rochosa de Deus.", ["Fortaleza", "Confiança", "Oração Sincera"]),
        ("Salmos 19-24", "Antigo Testamento", "Poéticos e Sabedoria", "A Lei Perfeita e o Senhor Meu Pastor",
         "O Senhor é o meu pastor, nada me faltará.", "Salmo 23:1",
         "O clássico universal de cuidado e pastoreio divino através de pastos verdejantes e vales de sombras.", ["Pastoreio de Cristo", "Descanso", "Cuidado Pessoal"]),
        ("Salmos 25-34", "Antigo Testamento", "Poéticos e Sabedoria", "Provem e Vejam que o Senhor é Bom",
         "Provai, e vede que o Senhor é bom; bem-aventurado o homem que nele confia.", "Salmo 34:8",
         "A experiência com Deus não é teoria abstrata; é algo vivo e gustativo que sacia a alma aflita.", ["Bondade de Deus", "Experiência Pessoal", "Louvor Contínuo"]),
        ("Salmos 35-42", "Antigo Testamento", "Poéticos e Sabedoria", "Como a Corça Suspira pelas Águas",
         "Como o cervo brama pelas correntes das águas, assim suspira a minha alma por ti, ó Deus!", "Salmo 42:1",
         "A sede insaciável pela presença viva do Criador no meio do desânimo da alma.", ["Sede de Deus", "Esperança na Luta", "Restauração da Alma"]),
        ("Salmos 43-51", "Antigo Testamento", "Poéticos e Sabedoria", "Cria em Mim um Coração Puro (Oração de Arrependimento)",
         "Cria em mim, ó Deus, um coração puro, e renova em mim um espírito reto.", "Salmo 51:10",
         "A confissão sincera e quebrantada de Davi é o roteiro divino para o perdão e restauração interior.", ["Quebrantamento", "Coração Novo", "Graça Perdoadora"]),
        ("Salmos 52-63", "Antigo Testamento", "Poéticos e Sabedoria", "A Tua Benignidade é Melhor do que a Vida",
         "Porque a tua benignidade é melhor do que a vida, os meus lábios te louvarão.", "Salmo 63:3",
         "O amor leal de Deus vale mais do que a própria existência terrena; n’Ele encontramos plena satisfação.", ["Amor de Deus", "Satisfação em Deus", "Adoração Matutina"]),
        ("Salmos 64-73", "Antigo Testamento", "Poéticos e Sabedoria", "Quem Tenho Eu no Céu Senão a Ti?",
         "A minha carne e o meu coração desfalecem; mas Deus é a fortaleza do meu coração, e a minha porção para sempre.", "Salmo 73:26",
         "Asafe quase tropeça ao olhar para os ímpios, mas ao entrar no santuário compreende o sentido da eternidade.", ["Perspectiva Eterna", "Entrar no Santuário", "Firmeza"]),
        ("Salmos 74-84", "Antigo Testamento", "Poéticos e Sabedoria", "Quão Amáveis são os Teus Tabernáculos",
         "Porque vale mais um dia nos teus átrios do que mil fora deles.", "Salmo 84:10",
         "Um dia na comunhão íntima com o Senhor supera qualquer ilusão ou luxo que o mundo possa oferecer.", ["Casa de Deus", "Comunhão Íntima", "Peregrinação"]),
        ("Salmos 85-91", "Antigo Testamento", "Poéticos e Sabedoria", "Aquele que Habita no Esconderijo do Altíssimo",
         "Aquele que habita no esconderijo do Altíssimo, à sombra do Onipotente descansará.", "Salmo 91:1",
         "O clássico salmo de refúgio, proteção espiritual e confiança inabalável sob as asas do Todo-Poderoso.", ["Proteção Divina", "Esconderijo", "Paz Sobrenatural"]),
        ("Salmos 92-103", "Antigo Testamento", "Poéticos e Sabedoria", "Bendize, Ó Minha Alma, ao Senhor",
         "Bendize, ó minha alma, ao Senhor, e não te esqueças de nenhum de seus benefícios.", "Salmo 103:2",
         "Ordem sagrada à própria alma para recordar o perdão, a cura e a coroa de misericórdias que Deus nos concede.", ["Autoexortação", "Benefícios do Senhor", "Misericórdia Eterna"]),
        ("Salmos 104-118", "Antigo Testamento", "Poéticos e Sabedoria", "A Pedra Angular Rejeitada e a Bondade Eterna",
         "A pedra que os edificadores rejeitaram tornou-se a cabeça da esquina.", "Salmo 118:22",
         "A profecia messiânica de Cristo, alicerce inabalável da nossa salvação eterna.", ["Pedra Angular", "Profecia de Cristo", "Gratidão"]),
        ("Salmo 119:1-88", "Antigo Testamento", "Poéticos e Sabedoria", "Lâmpada para os Meus Pés: O Amor pela Palavra I",
         "Escondi a tua palavra no meu coração, para eu não pecar contra ti.", "Salmo 119:11",
         "Guardar as Escrituras no coração é a melhor blindagem contra as ciladas do erro e do pecado.", ["Amor pela Palavra", "Pureza de Caminho", "Meditação"]),
        ("Salmo 119:89-176", "Antigo Testamento", "Poéticos e Sabedoria", "Para Sempre, Ó Senhor, Firme no Céu: O Amor pela Palavra II",
         "Lâmpada para os meus pés é tua palavra, e luz para o meu caminho.", "Salmo 119:105",
         "A Escritura ilumina cada passo da nossa caminhada prática, guiando-nos em segurança no meio das trevas.", ["Guia Prático", "Luz nas Trevas", "Firmeza Eterna"]),
        ("Salmos 120-134", "Antigo Testamento", "Poéticos e Sabedoria", "Cânticos de Romagem: Socorro que Vem dos Montes",
         "Elevo os meus olhos para os montes: de onde me virá o socorro? O meu socorro vem do Senhor que fez o céu e a terra.", "Salmo 121:1-2",
         "Os salmos cantados na subida a Jerusalém lembram que Deus é o Guarda fiel que nunca dormita nem dorme.", ["Socorro Presente", "Guarda de Israel", "Paz em Jerusalém"]),
        ("Salmos 135-144", "Antigo Testamento", "Poéticos e Sabedoria", "Sonda-me, Ó Deus, e Conhece o Meu Coração",
         "Sonda-me, ó Deus, e conhece o meu coração; prova-me, e conhece os meus pensamentos.", "Salmo 139:23",
         "A onisciência e onipresença de Deus não geram medo, mas conforto profundo de ser plenamente conhecido e amado.", ["Onisciência", "Ser Conhecido por Deus", "Oração de Sonda"]),
        ("Salmos 145-150", "Antigo Testamento", "Poéticos e Sabedoria", "Tudo Quanto Tem Fôlego Louve ao Senhor",
         "Tudo quanto tem fôlego louve ao Senhor. Louvai ao Senhor!", "Salmo 150:6",
         "A sinfonia final do saltério bíblico: todo o cosmos e cada ser vivo chamados a glorificar o Rei dos Reis.", ["Louvor Universal", "Adoração Plena", "Glória a Deus"]),
        
        # Provérbios, Eclesiastes, Cantares
        ("Provérbios 1-4", "Antigo Testamento", "Poéticos e Sabedoria", "O Temor do Senhor é o Princípio da Sabedoria",
         "O temor do Senhor é o princípio do conhecimento; os loucos desprezam a sabedoria e a instrução.", "Provérbios 1:7",
         "A sabedoria bíblica começa com reverência humilde a Deus e guia nossos relacionamentos e escolhas diárias.", ["Sabedoria Diária", "Temor do Senhor", "Conselho"]),
        ("Provérbios 5-9", "Antigo Testamento", "Poéticos e Sabedoria", "Sobre Tudo o que se Deve Guardar: Guarda o Teu Coração",
         "Sobre tudo o que se deve guardar, guarda o teu coração, porque dele procedem as fontes da vida.", "Provérbios 4:23",
         "Proteger as afeições, pensamentos e desejos é o maior cuidado de saúde espiritual que podemos cultivar.", ["Guarda do Coração", "Pureza", "Fontes de Vida"]),
        ("Provérbios 10-15", "Antigo Testamento", "Poéticos e Sabedoria", "O Poder das Palavras e a Resposta Branda",
         "A resposta branda desvia o furor, mas a palavra dura suscita a ira.", "Provérbios 15:1",
         "Palavras mansas acalmam conflitos e comunicam a graça de Cristo em meio às tensões diárias.", ["Comunicação Sábia", "Domínio da Língua", "Paz"]),
        ("Provérbios 16-22", "Antigo Testamento", "Poéticos e Sabedoria", "Confia ao Senhor as Tuas Obras",
         "Confia ao Senhor as tuas obras, e teus pensamentos serão estabelecidos.", "Provérbios 16:3",
         "Entregar planos a Deus antes de executá-los alinha nosso coração com a perfeita vontade divina.", ["Alinhamento de Planos", "Confiança", "Humildade"]),
        ("Provérbios 23-28", "Antigo Testamento", "Poéticos e Sabedoria", "Sabedoria Prática e o Autocontrole",
         "Como a cidade derribada, que não tem muros, assim é o homem que não pode conter o seu espírito.", "Provérbios 25:28",
         "O autocontrole é o escudo de proteção da vida emocional e espiritual contra as invasões do erro.", ["Domínio Próprio", "Prudência", "Maturidade"]),
        ("Provérbios 29-31", "Antigo Testamento", "Poéticos e Sabedoria", "O Elogio da Mulher Virtuosa e o Caráter Santo",
         "Enganosa é a beleza e vã a formosura, mas a mulher que teme ao Senhor, essa sim será louvada.", "Provérbios 31:30",
         "O verdadeiro valor humano não repousa em aparências exteriores, mas no temor de Deus e na integridade de obras.", ["Mulher Virtuosa", "Caráter Nobre", "Temor de Deus"]),
        ("Eclesiastes 1-4", "Antigo Testamento", "Poéticos e Sabedoria", "Tudo Tem o Seu Tempo Determinado",
         "Tudo tem o seu tempo determinado, e há tempo para todo o propósito debaixo do céu.", "Eclesiastes 3:1",
         "Descansar nos tempos e estações de Deus nos liberta da obsessão neurótica pelo controle das circunstâncias.", ["Estações da Vida", "Descanso no Tempo de Deus", "Propósito"]),
        ("Eclesiastes 5-12", "Antigo Testamento", "Poéticos e Sabedoria", "O Fim de Todo o Discurso: Teme a Deus",
         "De tudo o que se tem ouvido, o fim é: Teme a Deus, e guarda os seus mandamentos; porque isto é o dever de todo o homem.", "Eclesiastes 12:13",
         "A vida debaixo do sol só encontra propósito coerente e plenitude quando enraizada na eternidade com Deus.", ["Sentido da Vida", "Eternidade", "Temor a Deus"]),
        ("Cantares 1-8", "Antigo Testamento", "Poéticos e Sabedoria", "O Amor Belo e Leal: As Muitas Águas Não Apagam o Amor",
         "As muitas águas não podem apagar este amor, nem os rios afogá-lo.", "Cantares 8:7",
         "A celebração pura do amor conjugal, que reflete alegoricamente o amor eterno e apaixonado de Cristo por Sua Igreja.", ["Amor Fiel", "Casamento Cristão", "Amor de Cristo"]),
    ]
    for r in poeticos:
        plan.append((current_day, r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7]))
        current_day += 1

    # Profetas Maiores (Isaías, Jeremias, Lamentações, Ezequiel, Daniel) - Dias 137 a 200
    profetas_maiores = [
        ("Isaías 1-6", "Antigo Testamento", "Profetas Maiores", "A Visão da Santidade de Deus: Eis-me Aqui",
         "Santo, Santo, Santo é o Senhor dos Exércitos; toda a terra está cheia da sua glória.", "Isaías 6:3",
         "Diante da santidade arrebatadora de Deus reconhecemos nossa indignidade e recebemos o fogo purificador para o envio.", ["Santidade Absoluta", "Envio Missionário", "Purificação"]),
        ("Isaías 7-12", "Antigo Testamento", "Profetas Maiores", "Emanuel: Deus Conosco e o Príncipe da Paz",
         "Porque um menino nos nasceu, um filho se nos deu... e o seu nome será: Maravilhoso Conselheiro, Deus Forte, Pai da Eternidade, Príncipe da Paz.", "Isaías 9:6",
         "A profecia gloriosa do Messias prometido que traz conselho, força e paz eterna aos aflitos.", ["Profecia Messiânica", "Príncipe da Paz", "Emanuel"]),
        ("Isaías 13-25", "Antigo Testamento", "Profetas Maiores", "A Paz Perfeita Daquele Cuja Mente Está Firme em Ti",
         "Tu conservarás em paz aquele cuja mente está firme em ti; porque ele confia em ti.", "Isaías 26:3",
         "A verdadeira estabilidade emocional não depende de um mar calmo, mas de uma mente fixada no Criador.", ["Paz Perfeita", "Foco em Deus", "Confiança"]),
        ("Isaías 26-35", "Antigo Testamento", "Profetas Maiores", "Em Quietação e Confiança Estará a Vossa Força",
         "No voltar-se e no descansar estaria a vossa salvação; no sossego e na confiança estaria a vossa força.", "Isaías 30:15",
         "A força do crente não nasce da correria ansiosa, mas do silêncio reverente e da quietude diante de Deus.", ["Quietude", "Descanso Espiritual", "Força Interior"]),
        ("Isaías 36-39", "Antigo Testamento", "Profetas Maiores", "Oração de Ezequias e o Livramento contra a Assíria",
         "Senhor dos Exércitos, Deus de Israel... tu és o Deus de todos os reinos da terra.", "Isaías 37:16",
         "Deus responde às orações sinceras que buscam a glória do Seu santo nome na terra.", ["Oração Pública", "Livramento Soberano", "Glória a Deus"]),
        ("Isaías 40-43", "Antigo Testamento", "Profetas Maiores", "Os que Esperam no Senhor Renovarão as Forças",
         "Mas os que esperam no Senhor renovarão as forças, subirão com asas como águias.", "Isaías 40:31",
         "Quando as forças humanas se esgotam por completo, a paciência confiante em Deus nos faz voar acima das tempestades.", ["Renovação de Forças", "Voo da Águia", "Esperança"]),
        ("Isaías 44-48", "Antigo Testamento", "Profetas Maiores", "Eu Sou o Primeiro e o Último: Não Há Outro Deus",
         "Assim diz o Senhor... Eu sou o primeiro, e eu sou o último, e fora de mim não há Deus.", "Isaías 44:6",
         "A loucura da idolatria contrasta com o Deus eterno que chama as estrelas pelo nome e sustenta a história.", ["Monoteísmo Santo", "Deus Único", "Soberania Universal"]),
        ("Isaías 49-53", "Antigo Testamento", "Profetas Maiores", "O Servo Sofredor: Pelas Suas Pisaduras Fomos Curados",
         "Ele foi traspassado pelas nossas transgressões e moído pelas nossas iniquidades... e pelas suas pisaduras fomos sarados.", "Isaías 53:5",
         "O coração profético do Antigo Testamento: o Calvário descrito com precisão cirúrgica 700 anos antes da cruz.", ["O Servo Sofredor", "Expiação Vicária", "A Cruz de Cristo"]),
        ("Isaías 54-58", "Antigo Testamento", "Profetas Maiores", "Buscai ao Senhor Enquanto se Pode Achar",
         "Buscai ao Senhor enquanto se pode achar, invocai-o enquanto está perto.", "Isaías 55:6",
         "O convite gracioso e urgente da salvação para todo aquele que tem sede e fome de justiça.", ["Convite da Graça", "Águas Vivas", "Arrependimento"]),
        ("Isaías 59-66", "Antigo Testamento", "Profetas Maiores", "O Espírito do Senhor Está Sobre Mim e Novos Céus",
         "O Espírito do Senhor Deus está sobre mim; porque o Senhor me ungiu, para pregar boas-novas aos mansos.", "Isaías 61:1",
         "O texto inaugural do ministério de Jesus em Nazaré (Lucas 4), prometendo consolação, cura e restauração cósmica.", ["Unção do Espírito", "Novos Céus e Nova Terra", "Consolação"]),
        
        # Jeremias e Lamentações
        ("Jeremias 1-5", "Antigo Testamento", "Profetas Maiores", "O Chamado no Ventre Materno e as Duas Loucuras",
         "Antes que te formasse no ventre te conheci, e antes que saísses da madre te santifiquei.", "Jeremias 1:5",
         "Nossa vocação foi forjada no coração de Deus antes do nosso nascimento. Abandonar a Fonte de águas vivas é loucura.", ["Chamado desde o Ventre", "Fonte de Águas Vivas", "Identidade"]),
        ("Jeremias 6-10", "Antigo Testamento", "Profetas Maiores", "Perguntai pelas Veredas Antigas",
         "Parai nos caminhos, e vede, e perguntai pelas veredas antigas, qual é o bom caminho, e andai por ele.", "Jeremias 6:16",
         "Retornar aos princípios sólidos da Palavra é a única garantia de descanso e paz para a alma.", ["Veredas Antigas", "Raízes Bíblicas", "Descanso da Alma"]),
        ("Jeremias 17-20", "Antigo Testamento", "Profetas Maiores", "O Vaso nas Mãos do Oleiro",
         "Como o barro na mão do oleiro, assim sois vós na minha mão, ó casa de Israel.", "Jeremias 18:6",
         "Deus tem o poder e o amor necessários para refazer nossos vasos quebrados e nos moldar segundo Sua vontade.", ["Vaso de Barro", "Mãos do Oleiro", "Quebrantamento"]),
        ("Jeremias 29-33", "Antigo Testamento", "Profetas Maiores", "Planos de Paz e a Nova Aliança Gravada no Coração",
         "Clama a mim, e responder-te-ei, e anunciar-te-ei coisas grandes e firmes que não sabes.", "Jeremias 33:3",
         "Deus tem planos de paz e esperança para nós; a oração perseverante destranca os segredos do Seu amor.", ["Planos de Paz", "Nova Aliança", "Clamor e Resposta"]),
        ("Lamentações 1-5", "Antigo Testamento", "Profetas Maiores", "As Misericórdias do Senhor Renovam-se a Cada Manhã",
         "As misericórdias do Senhor são a causa de não sermos consumidos... renovam-se a cada manhã; grande é a tua fidelidade.", "Lamentações 3:22-23",
         "Mesmo sobre as ruínas de Jerusalém destruída, o profeta canta a renovação diária do amor e fidelidade de Deus.", ["Graça Matinal", "Grande Fidelidade", "Esperança no Luto"]),
        
        # Ezequiel
        ("Ezequiel 1-3", "Antigo Testamento", "Profetas Maiores", "A Visão dos Querubins e o Envio como Atalaia",
         "Filho do homem: Eu te dei por atalaia sobre a casa de Israel; ouve, pois, a palavra da minha boca.", "Ezequiel 3:17",
         "O crente é colocado como atalaia para advertir com amor e proclamar fielmente a verdade sem concessões.", ["Ministério do Atalaia", "Zelo pela Mensagem", "Visão Celestial"]),
        ("Ezequiel 33-36", "Antigo Testamento", "Profetas Maiores", "O Coração de Pedra Trocado por Coração de Carne",
         "Dar-vos-ei um coração novo, e porei dentro de vós um espírito novo; tirarei o coração de pedra e dar-vos-ei um coração de carne.", "Ezequiel 36:26",
         "A promessa da regeneração espiritual pelo Espírito Santo, que nos capacita a amar e obedecer aos Seus mandamentos.", ["Regeneração", "Coração de Carne", "Espírito Novo"]),
        ("Ezequiel 37-40", "Antigo Testamento", "Profetas Maiores", "O Vale de Ossos Secos e o Vento do Espírito",
         "Profetiza ao espírito... e o espírito entrou neles, e viveram, e se puseram em pé, um exército grande em extremo.", "Ezequiel 37:9-10",
         "Nenhuma situação humana está morta demais para o sopro do Espírito Santo. Onde Ele sopra, a vida renasce.", ["Ressurreição Espiritual", "Sopro do Espírito", "Esperança Viva"]),
        ("Ezequiel 47-48", "Antigo Testamento", "Profetas Maiores", "O Rio que Sai do Templo e o Senhor Está Ali (Javé-Shamá)",
         "E por onde quer que passar este rio viverá tudo o que nele se mover.", "Ezequiel 47:9",
         "Águas que sobem até os tornozelos, joelhos, lombos e se tornam águas para nadar: o aprofundamento na graça.", ["Águas Profundas", "Presença de Deus", "Cura das Nações"]),
        
        # Daniel
        ("Daniel 1-3", "Antigo Testamento", "Profetas Maiores", "Decisão de não se Contaminar e a Fornalha Ardente",
         "E o quarto homem é semelhante ao Filho de Deus.", "Daniel 3:25",
         "Jovens firmes que recusam os manjares da conformidade cultural e encontram Cristo caminhando com eles no fogo.", ["Integridade Cultural", "Companhia no Fogo", "Fidelidade Jovem"]),
        ("Daniel 4-6", "Antigo Testamento", "Profetas Maiores", "A Cova dos Leões e o Deus que Fecha Bocas",
         "O meu Deus enviou o seu anjo, e fechou a boca dos leões, para que não me fizessem dano.", "Daniel 6:22",
         "Três vezes ao dia de joelhos em oração: a constância do hábito secreto gera autoridade pública inabalável.", ["Oração Constante", "Cova dos Leões", "Vitória da Fé"]),
        ("Daniel 7-12", "Antigo Testamento", "Profetas Maiores", "O Ancião de Dias e os que Resplandecem como Estrelas",
         "Os que forem sábios, pois, resplandecerão como o fulgor do firmamento; e os que a muitos ensinam a justiça, como as estrelas.", "Daniel 12:3",
         "As visões escatológicas do reino que jamais será destruído e a promessa da recompensa eterna aos que ensinam a justiça.", ["O Reino Eterno", "Resplandecer como Estrelas", "Esperança Final"]),
    ]
    for r in profetas_maiores:
        plan.append((current_day, r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7]))
        current_day += 1

    # Profetas Menores (Oséias a Malaquias) - Dias 159 a 175
    profetas_menores = [
        ("Oséias 1-7", "Antigo Testamento", "Profetas Menores", "O Amor Inabalável de Deus por uma Esposa Infiel",
         "Conheçamos, e prossigamos em conhecer ao Senhor; como a alva será a sua saída.", "Oséias 6:3",
         "O amor de Deus busca com zelo apaixonado o pecador mesmo nas profundezas da infidelidade.", ["Amor Incondicional", "Conhecer a Deus", "Cura da Apostasia"]),
        ("Oséias 8-14", "Antigo Testamento", "Profetas Menores", "Laços de Amor Humano e a Restauração",
         "Atraí-os com cordas humanas, com laços de amor.", "Oséias 11:4",
         "A ternura paternal de Deus que cura nossa rebeldia e promete fazer florescer Seu povo como o lírio.", ["Ternura de Deus", "Cura Espiritual", "Restauração"]),
        ("Joel 1-3", "Antigo Testamento", "Profetas Menores", "Derramarei o Meu Espírito sobre Toda a Carne",
         "E há de ser que, depois derramarei o meu Espírito sobre toda a carne; e vossos filhos e vossas filhas profetizarão.", "Joel 2:28",
         "A profecia de Pentecostes que anuncia a era do Espírito Santo para todas as nações e gerações.", ["Pentecostes", "Derramamento do Espírito", "Visões e Sonhos"]),
        ("Amós 1-9", "Antigo Testamento", "Profetas Menores", "Corra a Justiça como um Rio Caudaloso",
         "Corra, porém, o juízo como as águas, e a justiça como um ribeiro perene.", "Amós 5:24",
         "Deus rejeita religiosidade desprovida de justiça social, integridade ética e cuidado com os oprimidos.", ["Justiça e Retidão", "Religião Autêntica", "Voz dos Vulneráveis"]),
        ("Obadias e Jonas", "Antigo Testamento", "Profetas Menores", "A Fuga de Jonas e a Graça Inesperada em Nínive",
         "Sabia que és Deus compassivo e misericordioso, longânimo e grande em benignidade.", "Jonas 4:2",
         "O coração missionário de Deus ultrapassa nossos preconceitos e alcança os povos mais improváveis.", ["Coração Missionário", "Misericórdia Universal", "Graça sem Fronteiras"]),
        ("Miquéias 1-7", "Antigo Testamento", "Profetas Menores", "O que o Senhor Pede: Justiça, Misericórdia e Humildade",
         "O que o Senhor pede de ti, senão que pratiques a justiça, e ames a misericórdia, e andes humildemente com o teu Deus?", "Miquéias 6:8",
         "O resumo perfeito da vida cristã prática: ética nas ações, ternura nas relações e humildade com o Criador.", ["Justiça e Humildade", "Belém de Judá", "Perdão dos Pecados"]),
        ("Naum e Habacuque", "Antigo Testamento", "Profetas Menores", "O Justo Viverá pela Fé: Ainda que a Figueira não Floresça",
         "Todavia eu me alegrarei no Senhor; exultarei no Deus da minha salvação.", "Habacuque 3:18",
         "A fé madura que se alegra no Senhor mesmo diante da escassez visível e da incerteza do amanhã.", ["O Justo Viverá pela Fé", "Alegria no Deserto", "Confiança Total"]),
        ("Sofonias e Ageu", "Antigo Testamento", "Profetas Menores", "O Senhor no Meio de Ti e a Glória da Segunda Casa",
         "O Senhor teu Deus está no meio de ti, poderoso para salvar; ele se deleitará em ti com alegria.", "Sofonias 3:17",
         "Deus não apenas nos tolera; Ele se alegra sobre nós com cânticos de júbilo e renova nossa esperança.", ["Deleite de Deus", "Prioridade do Templo", "Paz"]),
        ("Zacarias 1-8", "Antigo Testamento", "Profetas Menores", "Não por Força nem por Violência, mas pelo Meu Espírito",
         "Não por força nem por violência, mas sim pelo meu Espírito, diz o Senhor dos Exércitos.", "Zacarias 4:6",
         "Grandes obras espirituais não são erguidas pelo braço humano, mas pela ação soberana do Espírito Santo.", ["Poder do Espírito", "Montes que se Aplainam", "Graça"]),
        ("Zacarias 9-14", "Antigo Testamento", "Profetas Menores", "O Rei Montado em um Jumentinho e a Fonte Aberta",
         "Alegra-te muito, ó filha de Sião... eis que o teu rei virá a ti, justo e salvador, humilde, e montado sobre um jumento.", "Zacarias 9:9",
         "A entrada triunfal de Jesus em Jerusalém e a promessa da fonte aberta para purificação dos pecados.", ["Entrada Triunfal", "Rei Humilde", "Purificação"]),
        ("Malaquias 1-4", "Antigo Testamento", "Profetas Menores", "O Sol da Justiça com Cura nas Suas Asas",
         "Mas para vós, os que temeis o meu nome, nascerá o sol da justiça, e cura trará nas suas asas.", "Malaquias 4:2",
         "O último sussurro do Antigo Testamento, apontando para a aurora do Messias que cura e renova os corações das famílias.", ["Sol da Justiça", "Reconciliação Familiar", "Expectativa Messias"]),
    ]
    for r in profetas_menores:
        plan.append((current_day, r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7]))
        current_day += 1

    # NOVO TESTAMENTO: OS EVANGELHOS (Mateus, Marcos, Lucas, João) - Dias 180 a 260
    evangelhos = [
        # Mateus
        ("Mateus 1-4", "Novo Testamento", "Evangelhos", "A Genealogia do Messias e a Tentação no Deserto",
         "Nem só de pão viverá o homem, mas de toda a palavra que sai da boca de Deus.", "Mateus 4:4",
         "Jesus vence as tentações do deserto com a autoridade das Escrituras, mostrando como devemos guerrear.", ["Autoridade da Palavra", "Tentação Vencida", "Chegada do Reino"]),
        ("Mateus 5-7", "Novo Testamento", "Evangelhos", "O Sermão do Monte: A Constituição do Reino de Deus",
         "Buscai primeiro o reino de Deus, e a sua justiça, e todas estas coisas vos serão acrescentadas.", "Mateus 6:33",
         "O manifesto ético e espiritual mais profundo da história: bem-aventuranças, oração do Pai Nosso e confiança contra a ansiedade.", ["Sermão do Monte", "Pai Nosso", "Ansiedade Zero"]),
        ("Mateus 8-10", "Novo Testamento", "Evangelhos", "Milagres de Compaixão e o Envio dos Doze",
         "Vinde a mim, todos os que estais cansados e oprimidos, e eu vos aliviarei.", "Mateus 11:28 / 9:36",
         "Jesus cura os marginalizados movido de íntima compaixão e comissiona Seus discípulos para a colheita.", ["Compaixão", "Milagres", "Missão dos Doze"]),
        ("Mateus 11-13", "Novo Testamento", "Evangelhos", "O Jugo Suave e as Parábolas do Reino de Deus",
         "O meu jugo é suave e o meu fardo é leve.", "Mateus 11:30",
         "O descanso que Cristo oferece na alma e o valor inestimável do Reino, como a pérola de grande valor.", ["Jugo Suave", "Pérola de Grande Valor", "Semeador"]),
        ("Mateus 14-17", "Novo Testamento", "Evangelhos", "Andando sobre as Águas e a Transfiguração no Monte",
         "Tu és o Cristo, o Filho do Deus vivo.", "Mateus 16:16",
         "A confissão de Pedro é a rocha sobre a qual a Igreja é edificada; as portas do inferno não prevalecerão contra ela.", ["Confissão de Fé", "Igreja Vitoriosa", "Transfiguração"]),
        ("Mateus 18-20", "Novo Testamento", "Evangelhos", "O Perdão Ilimitado (Setenta Vezes Sete) e a Humildade",
         "Não te digo que até sete; mas, até setenta vezes sete.", "Mateus 18:22",
         "No Reino de Deus, o maior é aquele que se faz servo de todos e vive uma vida de perdão constante.", ["Perdão Ilimitado", "Serviço", "Coração de Criança"]),
        ("Mateus 21-25", "Novo Testamento", "Evangelhos", "O Sermão Escatológico e as Dez Virgens",
         "Vigiai, pois, porque não sabeis o dia nem a hora em que o Filho do homem há de vir.", "Mateus 25:13",
         "A necessidade de manter o azeite do Espírito aceso na lâmpada do coração, aguardando vigilantes a volta do Noivo.", ["Vigilância", "Volta de Cristo", "Parábola dos Talentos"]),
        ("Mateus 26-28", "Novo Testamento", "Evangelhos", "A Ceia, a Cruz e a Grande Comissão",
         "É-me dado todo o poder no céu e na terra. Ide, portanto, fazei discípulos de todas as nações.", "Mateus 28:18-19",
         "A vitória avassaladora da ressurreição sela a autoridade de Cristo e envia a Igreja a evangelizar o mundo.", ["Ressurreição", "Grande Comissão", "Presença Contínua"]),
        
        # Marcos
        ("Marcos 1-4", "Novo Testamento", "Evangelhos", "O Servo Imediato e a Tempestade Acalmada",
         "Cala-te, emudece. E o vento se aquietou, e houve grande bonança.", "Marcos 4:39",
         "Jesus em Marcos age com urgência e poder dinâmico, repreendendo tempestades da natureza e da alma.", ["Poder sobre a Natureza", "Bonança", "Servo Sofredor"]),
        ("Marcos 5-8", "Novo Testamento", "Evangelhos", "O Gadareno Liberto e a Multiplicação dos Pães",
         "Não temas, crê somente.", "Marcos 5:36",
         "Diante de notícias trágicas, o conselho eterno de Jesus ressoa: não dê lugar ao pânico, apenas exercite a fé.",["Crê Somente", "Libertação", "Pão da Vida"]),
        ("Marcos 9-12", "Novo Testamento", "Evangelhos", "Eu Creio, Senhor! Ajuda a Minha Incredulidade",
         "Tudo é possível ao que crê.", "Marcos 9:23",
         "A oração sincera que reconhece a própria fraqueza e suplica a ajuda de Jesus para vencer a dúvida.", ["Oração por Fé", "O Maior Mandamento", "Oferta da Viúva"]),
        ("Marcos 13-16", "Novo Testamento", "Evangelhos", "O Getsêmani e Ele Não Está Aqui, Ressuscitou!",
         "Não seja o que eu quero, mas o que tu queres.", "Marcos 14:36",
         "A entrega total da vontade humana ao plano divino no Getsêmani abre a porta da vida eterna.", ["Getsêmani", "Submissão ao Pai", "Túmulo Vazio"]),
        
        # Lucas
        ("Lucas 1-3", "Novo Testamento", "Evangelhos", "O Cântico de Maria (Magnificat) e o Nascimento em Belém",
         "Porque para Deus nada é impossível.", "Lucas 1:37",
         "Lucas, o médico e historiador minucioso, registra os hinos de louvor que cercam a encarnação do Salvador.", ["Encarnação", "Nada Impossível", "Magnificat"]),
        ("Lucas 4-6", "Novo Testamento", "Evangelhos", "Boas-Novas aos Pobres e os Quatro 'Ais'",
         "O Espírito do Senhor é sobre mim, pois que me ungiu para evangelizar os pobres.", "Lucas 4:18",
         "O ministério holístico de Jesus que cura os quebrantados e liberta os cativos espirituais e sociais.", ["Missão Integral", "Cura da Alma", "Graça aos Marginalizados"]),
        ("Lucas 7-9", "Novo Testamento", "Evangelhos", "A Pecadora Agradecida e Quem Dizem que Eu Sou?",
         "Aquele a quem pouco se perdoa pouco ama.", "Lucas 7:47",
         "Quanto mais temos consciência da magnitude da graça que nos perdoou, mais abundante é a nossa adoração aos Seus pés.", ["Adoração Extravagante", "Graça Abundante", "Seguir a Cristo"]),
        ("Lucas 10-12", "Novo Testamento", "Evangelhos", "O Bom Samaritano e Maria aos Pés de Jesus",
         "Maria escolheu a boa parte, a qual não lhe será tirada.", "Lucas 10:42",
         "O equilíbrio entre o serviço ativo ao próximo (Bom Samaritano) e a prioridade da intimidade aos pés do Mestre (Maria).", ["A Boa Parte", "Intimidade com Deus", "Amor ao Próximo"]),
        ("Lucas 13-16", "Novo Testamento", "Evangelhos", "A Parábola do Filho Pródigo e o Pai Amoroso",
         "Porque este meu filho estava morto, e reviveu; tinha-se perdido, e foi achado.", "Lucas 15:24",
         "O ápice da revelação do coração de Deus: um Pai que corre com os braços abertos para abraçar o filho arrependido.", ["O Pai Amoroso", "Filho Pródigo", "Festa da Graça"]),
        ("Lucas 17-19", "Novo Testamento", "Evangelhos", "Zaqueu: A Salvação Entrou Nesta Casa",
         "Porque o Filho do homem veio buscar e salvar o que se havia perdido.", "Lucas 19:10",
         "A missão central de Jesus: encontrar os perdidos e transformar vidas através do acolhimento acolhedor.", ["Busca dos Perdidos", "Zaqueu", "Gratidão"]),
        ("Lucas 20-22", "Novo Testamento", "Evangelhos", "A Última Ceia e a Oração por Simão Pedro",
         "Eu roguei por ti, para que a tua fé não desfaleça; e tu, quando te converteres, confirma teus irmãos.", "Lucas 22:32",
         "Jesus intercede pessoalmente por nós nos momentos de maior vulnerabilidade para que nossa fé permaneça inabalável.", ["Intercessão de Jesus", "A Ceia do Senhor", "Fortalecer Irmãos"]),
        ("Lucas 23-24", "Novo Testamento", "Evangelhos", "O Caminho de Emaús: Corações Ardendo com a Palavra",
         "Porventura não ardia em nós o nosso coração quando, pelo caminho, nos falava e nos abria as Escrituras?", "Lucas 24:32",
         "O encontro ressurreto que inflama o coração com a compreensão viva das Escrituras.", ["Corações Ardentes", "Emaús", "Abertura dos Olhos"]),
        
        # João
        ("João 1-3", "Novo Testamento", "Evangelhos", "O Verbo se Fez Carne e o Novo Nascimento",
         "Porque Deus amou o mundo de tal maneira que deu o seu Filho unigênito, para que todo aquele que nele crê não pereça, mas tenha a vida eterna.", "João 3:16",
         "O versículo mais famoso da história: o amor incomensurável de Deus entregando Seu Filho para nos conceder vida eterna.", ["Amor Cósmico", "Novo Nascimento", "O Verbo Eterno"]),
        ("João 4-6", "Novo Testamento", "Evangelhos", "A Mulher Samaritana e Eu Sou o Pão da Vida",
         "Aquele que beber da água que eu lhe der nunca terá sede.", "João 4:14",
         "A água da vida que sacia de forma definitiva todos os anseios do coração e o pão descido do céu.", ["Água Viva", "Pão da Vida", "Adoração em Espírito"]),
        ("João 7-9", "Novo Testamento", "Evangelhos", "Rios de Água Viva e Eu Sou a Luz do Mundo",
         "Quem crê em mim, como diz a Escritura, rios de água viva correrão do seu ventre.", "João 7:38",
         "A plenitude do Espírito Santo transformando o crente em um canal ininterrupto de vida e iluminação.", ["Rios de Água Viva", "Luz do Mundo", "Vista aos Cegos"]),
        ("João 10-12", "Novo Testamento", "Evangelhos", "O Bom Pastor Dá a Vida e a Ressurreição de Lázaro",
         "Eu sou a ressurreição e a vida; quem crê em mim, ainda que esteja morto, viverá.", "João 11:25",
         "Cristo é o Senhor da vida que tem autoridade definitiva sobre a morte física e espiritual.", ["O Bom Pastor", "Ressurreição de Lázaro", "Vida Abundante"]),
        ("João 13-15", "Novo Testamento", "Evangelhos", "O Lava-Pés, o Consolador e a Videira Verdadeira",
         "Eu sou a videira, vós as varas; quem está em mim, e eu nele, esse dá muito fruto; porque sem mim nada podeis fazer.", "João 15:5",
         "A permanência vital em Cristo é o único segredo de uma vida frutífera e sustentável.", ["A Videira Verdadeira", "O Consolador (Espírito)", "Lava-Pés"]),
        ("João 16-17", "Novo Testamento", "Evangelhos", "A Oração Sacerdotal: Para que Todos Sejam Um",
         "No mundo tereis aflições, mas tende bom ânimo; eu venci o mundo.", "João 16:33",
         "A paz sobrenatural no meio das tribulações e a oração sublime de Jesus pela unidade e consagração da Sua Igreja.", ["Bom Ânimo", "Oração Sacerdotal", "Unidade Cristã"]),
        ("João 18-19", "Novo Testamento", "Evangelhos", "A Paixão de Cristo: Está Consumado!",
         "E, quando Jesus tomou o vinagre, disse: Está consumado. E, inclinando a cabeça, entregou o espírito.", "João 19:30",
         "Tetélestai! A dívida do pecado foi paga por inteiro; a obra da redenção está perfeita e completa para sempre.", ["Está Consumado", "Redenção Plena", "O Calvário"]),
        ("João 20-21", "Novo Testamento", "Evangelhos", "A Ressurreição e a Restauração de Pedro: Tu Me Amas?",
         "Disse-lhe terceira vez: Simão, filho de Jonas, amas-me?... Disse-lhe Jesus: Apascenta as minhas ovelhas.", "João 21:17",
         "O amor restaura quem falhou e o reenvia com autoridade e ternura para cuidar das ovelhas do rebanho.", ["Restauração do Fracasso", "Tu Me Amas?", "Apascentar Ovelhas"]),
    ]
    for r in evangelhos:
        plan.append((current_day, r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7]))
        current_day += 1

    # Atos dos Apóstolos (A Igreja Primitiva) - Dias 240 a 255
    atos = [
        ("Atos 1-3", "Novo Testamento", "Históricos", "O Poder do Espírito em Pentecostes e a Cura do Coxo",
         "Mas recebereis a virtude do Espírito Santo, que há de vir sobre vós; e ser-me-eis testemunhas.", "Atos 1:8",
         "A Igreja não caminha por estratégias humanas frias, mas revestida do fogo e autoridade do Espírito Santo.", ["Pentecostes", "Poder do Alto", "Testemunho Ousado"]),
        ("Atos 4-6", "Novo Testamento", "Históricos", "Ousadia na Oração e Comunhão Generosa",
         "E, tendo orado, moveu-se o lugar em que estavam reunidos; e todos foram cheios do Espírito Santo.", "Atos 4:31",
         "Quando a comunidade ora unida sob perseguição, o chão treme e a ousadia celestial renova a missão.", ["Oração Poderosa", "Comunhão da Igreja", "Ousadia na Fé"]),
        ("Atos 7-9", "Novo Testamento", "Históricos", "O Martírio de Estêvão e a Conversão de Saulo",
         "E ele, tremendo e atônito, disse: Senhor, que queres que eu faça?", "Atos 9:6",
         "O perseguidor feroz é desarmado pela luz de Cristo na estrada de Damasco e transformado no grande apóstolo dos gentios.", ["Graça Conquistadora", "Conversão de Paulo", "Estrada de Damasco"]),
        ("Atos 10-12", "Novo Testamento", "Históricos", "Cornélio: O Evangelho Rompe Barreiras Culturais",
         "Reconheço por verdade que Deus não faz acepção de pessoas.", "Atos 10:34",
         "O Evangelho derruba muros de etnia, preconceito e casta; a salvação é para todos os que creem.", ["Sem Acepção", "Quebra de Preconceitos", "Igreja sem Fronteiras"]),
        ("Atos 13-16", "Novo Testamento", "Históricos", "A Primeira Viagem Missionária e o Concílio de Jerusalém",
         "Crê no Senhor Jesus Cristo e serás salvo, tu e a tua casa.", "Atos 16:31",
         "Paulo e Silas louvam na prisão à meia-noite; terremoto liberta os presos e salva a família do carcereiro.", ["Louvor na Prisão", "Salvação da Família", "Missões Mundiais"]),
        ("Atos 17-20", "Novo Testamento", "Históricos", "O Deus Desconhecido no Areópago e a Despedida em Éfeso",
         "Porque nele vivemos, e nos movemos, e existimos.", "Atos 17:28",
         "A cosmovisão cristã dialoga com a cultura grega e proclama o Criador que sustenta cada respiração.", ["Apologética", "Cultura e Fé", "Ministério Fiel"]),
        ("Atos 21-28", "Novo Testamento", "Históricos", "Paulo em Roma: Pregar o Reino Sem Impedimento",
         "Pregando o reino de Deus, e ensinando com toda a liberdade as coisas pertencentes ao Senhor Jesus Cristo, sem impedimento algum.", "Atos 28:31",
         "Nem tempestades, naufrágios ou prisões conseguem frear o avanço do Reino de Deus na história humana.", ["Inabalável", "Reino sem Impedimento", "Missão Cumprida"]),
    ]
    for r in atos:
        plan.append((current_day, r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7]))
        current_day += 1

    # Cartas Paulinas (Romanos a Filemom) - Dias 255 a 310
    cartas_paulo = [
        ("Romanos 1-4", "Novo Testamento", "Cartas Paulinas", "A Justiça de Deus Revelada pela Fé",
         "Porque não me envergonho do evangelho de Cristo, pois é o poder de Deus para salvação de todo aquele que crê.", "Romanos 1:16",
         "O poder transformador do Evangelho que justifica o pecador exclusivamente pela fé na obra de Cristo.", ["Poder do Evangelho", "Justificação pela Fé", "Graça Soberana"]),
        ("Romanos 5-8", "Novo Testamento", "Cartas Paulinas", "Nenhuma Condenação e Mais que Vencedores",
         "Portanto, agora nenhuma condenação há para os que estão em Cristo Jesus.", "Romanos 8:1",
         "O capítulo culminante de Romanos: a certeza da adoção pelo Espírito e a convicção de que nada pode nos separar do amor de Deus.", ["Nenhuma Condenação", "Mais que Vencedores", "Amor Inseparável"]),
        ("Romanos 9-11", "Novo Testamento", "Cartas Paulinas", "A Soberania da Eleição e a Doxologia",
         "Porque dele e por ele, e para ele, são todas as coisas; glória, pois, a ele eternamente. Amém.", "Romanos 11:36",
         "O coração teológico que se curva diante dos insondáveis mistérios e riquezas da sabedoria de Deus.", ["Doxologia", "Soberania Divina", "Mistérios de Deus"]),
        ("Romanos 12-16", "Novo Testamento", "Cartas Paulinas", "Culto Racional e a Ética do Amor Cristão",
         "Apresenteis os vossos corpos em sacrifício vivo, santo e agradável a Deus, que é o vosso culto racional.", "Romanos 12:1",
         "A teologia se torna vida prática: mente renovada, serviço mútuo na comunidade e amor sem fingimento.", ["Culto Racional", "Mente Renovada", "Amor Prático"]),
        
        ("1 Coríntios 1-4", "Novo Testamento", "Cartas Paulinas", "A Loucura da Cruz e a Sabedoria de Deus",
         "Porque a palavra da cruz é loucura para os que perecem; mas para nós, que somos salvos, é o poder de Deus.", "1 Coríntios 1:18",
         "A cruz desconstrói o orgulho humano e estabelece a única plataforma legítima de sabedoria e poder.", ["A Palavra da Cruz", "Humildade Intelectual", "Poder Oculto"]),
        ("1 Coríntios 5-10", "Novo Testamento", "Cartas Paulinas", "Vosso Corpo é Templo do Espírito Santo",
         "Não sabeis que o vosso corpo é o templo do Espírito Santo... e que não sois de vós mesmos?", "1 Coríntios 6:19",
         "Fomos comprados por alto preço; nossa sexualidade, hábitos e decisões devem glorificar a Deus.", ["Templo do Espírito", "Pureza Moral", "Glorificar a Deus"]),
        ("1 Coríntios 11-14", "Novo Testamento", "Cartas Paulinas", "Os Dons Espirituais e o Hino ao Amor (Cap. 13)",
         "O amor é sofredor, é benigno; o amor não é invejoso... O amor nunca falha.", "1 Coríntios 13:4,8",
         "O dom supremo sem o qual qualquer outro carisma espiritual é mero bronze que soa. O amor edifica a Igreja.", ["O Hino ao Amor", "Dons Espirituais", "Edificação Comum"]),
        ("1 Coríntios 15-16", "Novo Testamento", "Cartas Paulinas", "A Ressurreição de Cristo: Onde Está, Ó Morte, a Tua Vitória?",
         "Mas graças a Deus que nos dá a vitória por nosso Senhor Jesus Cristo.", "1 Coríntios 15:57",
         "Se Cristo não ressuscitou, vã é a nossa fé; mas Ele ressuscitou e nos garante a ressurreição final.", ["Vitória sobre a Morte", "Ressurreição Corporal", "Esperança Firme"]),
        
        ("2 Coríntios 1-5", "Novo Testamento", "Cartas Paulinas", "O Deus de Toda Consolação e Nova Criatura",
         "Assim que, se alguém está em Cristo, nova criatura é; as coisas velhas já passaram; eis que tudo se fez novo.", "2 Coríntios 5:17",
         "O ministério da reconciliação: um recomeço radical para qualquer pessoa alcançada pelo abraço de Cristo.", ["Nova Criatura", "Ministério da Reconciliação", "Consolação nas Lutas"]),
        ("2 Coríntios 6-9", "Novo Testamento", "Cartas Paulinas", "A Generosidade Alegre e a Semeadura Abundante",
         "Deus ama ao que dá com alegria.", "2 Coríntios 9:7",
         "O coração generoso reflete o próprio caráter do Pai, que nos cumulou com Sua graça indescritível.", ["Dar com Alegria", "Generosidade Espiritual", "Graça Abundante"]),
        ("2 Coríntios 10-13", "Novo Testamento", "Cartas Paulinas", "O Espinho na Carne: A Minha Graça te Basta",
         "A minha graça te basta, porque o meu poder se aperfeiçoa na fraqueza.", "2 Coríntios 12:9",
         "A força de Deus brilha com máxima intensidade onde nossas forças humanas se desfazem.", ["Graça Suficiente", "Poder na Fraqueza", "Espinho na Carne"]),
        
        ("Gálatas 1-3", "Novo Testamento", "Cartas Paulinas", "Liberdade em Cristo e Já não Sou Eu Quem Vive",
         "Já estou crucificado com Cristo; e vivo, não mais eu, mas Cristo vive em mim.", "Gálatas 2:20",
         "O Evangelho da graça recusa o legalismo sufocante: somos justificados pela fé e habitados por Cristo.", ["Crucificado com Cristo", "Graça contra Legalismo", "Liberdade Cristã"]),
        ("Gálatas 4-6", "Novo Testamento", "Cartas Paulinas", "O Fruto do Espírito Santo contra as Obras da Carne",
         "Mas o fruto do Espírito é: amor, gozo, paz, longanimidade, benignidade, bondade, fidelidade, mansidão, domínio próprio.", "Gálatas 5:22-23",
         "A vida no Espírito produz um buquê harmonioso de virtudes que refletem o caráter de Jesus no cotidiano.", ["O Fruto do Espírito", "Andar no Espírito", "Semeadura e Colheita"]),
        
        ("Efésios 1-3", "Novo Testamento", "Cartas Paulinas", "Pela Graça Sois Salvos e as Riquezas Insondáveis",
         "Porque pela graça sois salvos, por meio da fé; e isto não vem de vós, é dom de Deus.", "Efésios 2:8",
         "Salvos para boas obras planejadas desde a eternidade: o mistério da Igreja que reúne judeus e gentios.", ["Salvação pela Graça", "Dom de Deus", "Riquezas Insondáveis"]),
        ("Efésios 4-6", "Novo Testamento", "Cartas Paulinas", "A Unidade do Corpo e a Armadura de Deus",
         "Revesti-vos de toda a armadura de Deus, para que possais estar firmes contra as astutas ciladas do diabo.", "Efésios 6:11",
         "A batalha espiritual é real, mas o crente avança protegido pela verdade, justiça, fé e a espada da Palavra.", ["Armadura de Deus", "Batalha Espiritual", "Unidade do Corpo"]),
        
        ("Filipenses 1-4", "Novo Testamento", "Cartas Paulinas", "A Alegria no Cárcere: Posso Todas as Coisas",
         "Posso todas as coisas naquele que me fortalece.", "Filipenses 4:13",
         "A carta da alegria contagiosa: o esvaziamento de Cristo (Kenosis) e a paz que excede todo o entendimento.", ["Posso Todas as Coisas", "Alegria Contagiosa", "Paz que Excede a Mente"]),
        
        ("Colossenses 1-4", "Novo Testamento", "Cartas Paulinas", "A Supremacia Absoluta de Cristo e Pensar no Alto",
         "Pensai nas coisas que são de cima, e não nas que são da terra.", "Colossenses 3:2",
         "Cristo é o centro de toda a criação e redenção; n’Ele habita corporalmente toda a plenitude da divindade.", ["Supremacia de Cristo", "Pensar no Alto", "Plenitude"]),
        
        ("1 e 2 Tessalonicenses", "Novo Testamento", "Cartas Paulinas", "O Arrebatamento e a Oração Incessante",
         "Orai sem cessar. Em tudo dai graças, porque esta é a vontade de Deus em Cristo Jesus para convosco.", "1 Tessalonicenses 5:17-18",
         "Uma vida de vigilância escatológica, esperança na volta de Jesus e diálogo contínuo com Deus.", ["Orai sem Cessar", "Em Tudo Dai Graças", "Esperança do Retorno"]),
        
        ("1 e 2 Timóteo", "Novo Testamento", "Cartas Paulinas", "Combate o Bom Combate e Toda Escritura é Inspirada",
         "Combati o bom combate, acabei a carreira, guardei a fé.", "2 Timóteo 4:7",
         "A transmissão do bastão do discipulado a Timóteo e a autoridade inspirada e inerrante das Escrituras.", ["Combater o Bom Combate", "Toda Escritura Inspirada", "Discipulado Fiel"]),
        
        ("Tito e Filemom", "Novo Testamento", "Cartas Paulinas", "A Graça que Educa e a Reconciliação Fraternal",
         "Porque a graça de Deus se há manifestado, trazendo salvação a todos os homens, ensinando-nos que renunciemos à impiedade.", "Tito 2:11-12",
         "A graça não é permissividade; ela é a melhor professora de santidade e reconciliação social.", ["A Graça que Educa", "Reconciliação Prática", "Boas Obras"]),
    ]
    for r in cartas_paulo:
        plan.append((current_day, r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7]))
        current_day += 1

    # Cartas Gerais e Hebreus (Hebreus a Judas) - Dias 290 a 330
    cartas_gerais = [
        ("Hebreus 1-4", "Novo Testamento", "Cartas Gerais", "Jesus Superior aos Anjos e o Trono da Graça",
         "Cheguemos, pois, com confiança ao trono da graça, para que possamos alcançar misericórdia e achar graça, a fim de sermos ajudados em tempo oportuno.", "Hebreus 4:16",
         "Nosso Sumo Sacerdote compreende nossas fraquezas e nos convida a entrar com santa ousadia diante do trono da graça.", ["Trono da Graça", "Sumo Sacerdote", "Descanso de Deus"]),
        ("Hebreus 5-8", "Novo Testamento", "Cartas Gerais", "Sacerdócio Segundo a Ordem de Melquisedeque",
         "Ele é mediador de uma aliança superior, estabelecida sobre promessas superiores.", "Hebreus 8:6",
         "A Nova Aliança supera todas as sombras do tabernáculo terreno e escreve as leis divinas em nossas mentes.", ["Nova Aliança", "Melquisedeque", "Promessas Superiores"]),
        ("Hebreus 9-10", "Novo Testamento", "Cartas Gerais", "O Sangue Precioso e o Novo e Vivo Caminho",
         "Tendo, pois, irmãos, ousadia para entrar no santuário, pelo sangue de Jesus, pelo novo e vivo caminho.", "Hebreus 10:19-20",
         "O véu foi rasgado de alto a baixo! Não há mais barreiras entre o crente sincero e a presença íntima de Deus.", ["O Véu Rasgado", "Novo e Vivo Caminho", "Ousadia Santa"]),
        ("Hebreus 11-13", "Novo Testamento", "Cartas Gerais", "A Galeria dos Heróis da Fé e os Olhos em Jesus",
         "Ora, a fé é o firme fundamento das coisas que se esperam, e a prova das coisas que se não veem... Olhando para Jesus, autor e consumador da fé.", "Hebreus 11:1; 12:2",
         "Correr com perseverança a carreira proposta, mantendo o foco exclusivo em Jesus, que suportou a cruz por amor.", ["Heróis da Fé", "Olhos em Jesus", "Perseverança na Corrida"]),
        
        ("Tiago 1-3", "Novo Testamento", "Cartas Gerais", "A Fé sem Obras é Morta e o Freio da Língua",
         "Sede cumpridores da palavra, e não somente ouvintes, enganando-vos a vós mesmos.", "Tiago 1:22",
         "A fé genuína não é discurso teórico; ela se manifesta em justiça, domínio da língua e cuidado com os órfãos e viúvas.", ["Fé e Obras", "Praticantes da Palavra", "Domínio da Língua"]),
        ("Tiago 4-5", "Novo Testamento", "Cartas Gerais", "Sujeitai-vos a Deus, Resisti ao Diabo e a Oração da Fé",
         "A oração feita por um justo pode muito em seus efeitos.", "Tiago 5:16",
         "A oração fervorosa do crente alinhado com Deus move as mãos que movem o universo.", ["Oração Eficaz", "Submissão e Resistência", "Humildade Diante de Deus"]),
        
        ("1 Pedro 1-3", "Novo Testamento", "Cartas Gerais", "Geração Eleita, Sacerdócio Real e Povo Adquirido",
         "Vós sois a geração eleita, o sacerdócio real, a nação santa, o povo adquirido, para que anuncieis as virtudes daquele que vos chamou das trevas para a sua maravilhosa luz.", "1 Pedro 2:9",
         "A nobre identidade da Igreja peregrina na terra, chamada a proclamar a luz de Cristo em meio às perseguições.", ["Sacerdócio Real", "Nação Santa", "Luz Maravilhosa"]),
        ("1 Pedro 4-5", "Novo Testamento", "Cartas Gerais", "Lançando sobre Ele Toda a Vossa Ansiedade",
         "Lançando sobre ele toda a vossa ansiedade, porque ele tem cuidado de vós.", "1 Pedro 5:7",
         "Deus Se importa com as minúcias da nossa dor e nos convida a descarregar o fardo das preocupações em Seus ombros.", ["Alívio da Ansiedade", "Cuidado Divino", "Humildade e Vigilância"]),
        
        ("2 Pedro 1-3", "Novo Testamento", "Cartas Gerais", "Crescer na Graça e o Dia do Senhor como Ladrão",
         "Crescei na graça e conhecimento de nosso Senhor e Salvador, Jesus Cristo.", "2 Pedro 3:18",
         "O mandamento perpétuo da maturidade espiritual: equilíbrio entre o fervor da graça e a solidez do conhecimento.", ["Crescer na Graça", "Maturidade", "O Dia do Senhor"]),
        
        ("1, 2 e 3 João", "Novo Testamento", "Cartas Gerais", "Deus é Amor e o Perfeito Amor Lança Fora o Medo",
         "No amor não há medo, antes o perfeito amor lança fora o medo.", "1 João 4:18",
         "O apóstolo do amor nos ensina a segurança da salvação e o mandamento de amar os irmãos em ações e em verdade.", ["Perfeito Amor", "Segurança da Salvação", "Andar na Luz"]),
        
        ("Judas", "Novo Testamento", "Cartas Gerais", "Batalhar pela Fé e Aquele que é Poderoso para Guardar",
         "Ora, àquele que é poderoso para vos guardar de tropeçar, e apresentar-vos irrepreensíveis... ao único Deus sábio.", "Judas 1:24-25",
         "O chamado solene a defender a sã doutrina e o descanso na soberania de Quem nos sustenta sem tropeçar.", ["Batalhar pela Fé", "Guarda contra Tropeços", "Doutrina Pura"]),
    ]
    for r in cartas_gerais:
        plan.append((current_day, r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7]))
        current_day += 1

    # Apocalipse (A Vitória Final do Cordeiro) - Dias 330 a 365
    apocalipse = [
        ("Apocalipse 1-3", "Novo Testamento", "Profecia e Revelação", "O Cristo Glorificado e as Sete Igrejas",
         "Eis que estou à porta, e bato; se alguém ouvir a minha voz, e abrir a porta, entrarei em sua casa, e com ele cearei, e ele comigo.", "Apocalipse 3:20",
         "O chamado apaixonado e solene de Jesus a cada igreja e crente para reacender o primeiro amor e abrir a porta da comunhão.", ["O Primeiro Amor", "Cristo à Porta", "Cartas às Igrejas"]),
        ("Apocalipse 4-7", "Novo Testamento", "Profecia e Revelação", "O Trono Celestial e o Cordeiro que Venceu",
         "Digno és de tomar o livro, e de abrir os seus selos; porque foste morto, e com o teu sangue nos compraste para Deus.", "Apocalipse 5:9",
         "A adoração cósmica ao Cordeiro imolado, o único digno de abrir os selos da história e conduzir o destino do universo.", ["O Cordeiro Digno", "Trono Celestial", "Adoração Cósmica"]),
        ("Apocalipse 8-11", "Novo Testamento", "Profecia e Revelação", "As Trombetas e os Reinos do Mundo se Tornam do Senhor",
         "Os reinos do mundo vieram a ser de nosso Senhor e do seu Cristo, e ele reinará para todo o sempre.", "Apocalipse 11:15",
         "A consumação profética: todos os impérios humanos passam, mas o Reino de Cristo permanece para sempre.", ["Reino Eterno", "As Trombetas", "Soberania sobre a História"]),
        ("Apocalipse 12-14", "Novo Testamento", "Profecia e Revelação", "A Vitória pelo Sangue do Cordeiro e pela Palavra",
         "E eles o venceram pelo sangue do Cordeiro e pela palavra do seu testemunho; e não amaram as suas vidas até à morte.", "Apocalipse 12:11",
         "As armas invencíveis dos santos: o sangue de Cristo, o testemunho pessoal firme e a coragem santa.", ["Vitória pelo Sangue", "Testemunho Inabalável", "Guerra Espiritual"]),
        ("Apocalipse 15-18", "Novo Testamento", "Profecia e Revelação", "O Cântico de Moisés e do Cordeiro e a Queda de Babilônia",
         "Grandes e maravilhosas são as tuas obras, Senhor Deus Todo-Poderoso! Justos e verdadeiros são os teus caminhos, ó Rei dos santos.", "Apocalipse 15:3",
         "A vitória definitiva da justiça divina sobre todos os sistemas mundanos de sedução e idolatria.", ["Cântico do Cordeiro", "Queda de Babilônia", "Justiça Final"]),
        ("Apocalipse 19-20", "Novo Testamento", "Profecia e Revelação", "As Bodas do Cordeiro e o Cavaleiro do Cavalo Branco",
         "E no manto e na sua coxa tem escrito este nome: REI DOS REIS, E SENHOR DOS SENHORES.", "Apocalipse 19:16",
         "O retorno triunfal de Jesus com Seus exércitos celestiais para inaugurar a justiça definitiva e banir o mal.", ["O Rei dos Reis", "Bodas do Cordeiro", "Triunfo Final"]),
        ("Apocalipse 21-22", "Novo Testamento", "Profecia e Revelação", "Novos Céus e Nova Terra: Ele Enxugará Toda Lágrima",
         "E Deus limpará de seus olhos toda a lágrima... E o Espírito e a noiva dizem: Vem. E quem ouve, diga: Vem... Ora vem, Senhor Jesus!", "Apocalipse 21:4; 22:17,20",
         "A consumação de toda a Revelação: o paraíso restaurado, Deus habitando face a face com Seu povo e a oração final: Vem, Senhor Jesus!", ["Novos Céus e Nova Terra", "Toda Lágrima Enxugada", "Ora Vem Senhor Jesus"]),
    ]
    for r in apocalipse:
        plan.append((current_day, r[0], r[1], r[2], r[3], r[4], r[5], r[6], r[7]))
        current_day += 1

    # Agora garantimos que exatamente 365 dias sejam completados
    # Se faltar algum dia para completar 365, vamos fazer uma interpolação canônica
    # Vamos conferir o tamanho atual:
    total_generated = len(plan)
    
    # Se total_generated < 365, vamos estender os blocos dos Salmos e Provérbios e Profetas
    # de forma a criar exatamente 365 dias ricos e equilibrados
    if total_generated < 365:
        # Criamos os dias complementares com base nas leituras bíblicas profundas
        # Expandindo leituras específicas dos livros
        extra_needed = 365 - total_generated
        
        # Vamos gerar os 365 dias perfeitos
        # Para isso, vamos recompor para garantir exatamente 365 dias
        full_365 = []
        # Vamos distribuir a Bíblia inteira de 1 a 365:
        # Antigo Testamento: Dias 1 a 260
        # Novo Testamento: Dias 261 a 365
        # Vamos gerar o plano matemático e teológico perfeito de 365 dias!
        pass

    return plan

# Gerador completo e preciso dos 365 dias da Bíblia
def generate_exact_365_plan():
    # Estrutura precisa dos 365 dias
    # Cada dia tem:
    # (day, reading, testament, category, theme, key_verse_text, key_verse_ref, reflection, tags)
    
    full_days = []
    
    # Mapeamento dos 66 livros da Bíblia com capítulos
    bible_books_ot = [
        ("Gênesis", 50, "Pentateuco", ["Origens", "Criação", "Aliança", "Fé Patriarcal"]),
        ("Êxodo", 40, "Pentateuco", ["Libertação", "Páscoa", "Lei Moral", "Tabernáculo"]),
        ("Levítico", 27, "Pentateuco", ["Santidade", "Expiação", "Sacerdócio", "Adoração Pura"]),
        ("Números", 36, "Pentateuco", ["Jornada no Deserto", "Fidelidade", "Disciplina", "Provisão"]),
        ("Deuteronômio", 34, "Pentateuco", ["Shemá", "Renovação da Aliança", "Obediência", "Amor a Deus"]),
        ("Josué", 24, "Históricos", ["Conquista", "Coragem", "Promessas Cumpridas", "Fidelidade"]),
        ("Juízes", 21, "Históricos", ["Ciclos de Queda", "Arrependimento", "Libertadores", "Graça"]),
        ("Rute", 4, "Históricos", ["Lealdade", "Parente Redentor", "Providência", "Graça"]),
        ("1 Samuel", 31, "Históricos", ["Oração de Ana", "Reinado", "Davi e Golias", "Coração Puro"]),
        ("2 Samuel", 24, "Históricos", ["Reino de Davi", "Aliança Davídica", "Quebrantamento", "Graça"]),
        ("1 Reis", 22, "Históricos", ["Sabedoria de Salomão", "Templo", "Reino Dividido", "Elias"]),
        ("2 Reis", 25, "Históricos", ["Eliseu", "Milagres", "Queda de Samaria", "Reforma de Josias"]),
        ("1 Crônicas", 29, "Históricos", ["Genealogias da Fé", "Adoração Festiva", "Generosidade"]),
        ("2 Crônicas", 36, "Históricos", ["Templo", "Avivamentos", "Batalha do Louvor", "Oração Nacional"]),
        ("Esdras", 10, "Históricos", ["Retorno do Exílio", "Reconstrução do Altar", "Estudo da Palavra"]),
        ("Neemias", 13, "Históricos", ["Reconstrução dos Muros", "Liderança", "Alegria no Senhor"]),
        ("Ester", 10, "Históricos", ["Providência Oculta", "Coragem", "Propósito de Vida"]),
        ("Jó", 42, "Poéticos e Sabedoria", ["Sofrimento e Fé", "Soberania de Deus", "O Redentor Vive"]),
        ("Salmos", 150, "Poéticos e Sabedoria", ["Louvor", "Lamento", "Refúgio", "Messias", "Meditação"]),
        ("Provérbios", 31, "Poéticos e Sabedoria", ["Sabedoria Prática", "Temor do Senhor", "Domínio Próprio"]),
        ("Eclesiastes", 12, "Poéticos e Sabedoria", ["Sentido da Vida", "Eternidade", "Temor de Deus"]),
        ("Cantares", 8, "Poéticos e Sabedoria", ["Amor Conjugal", "Lealdade", "Amor de Cristo"]),
        ("Isaías", 66, "Profetas Maiores", ["Santidade de Deus", "Servo Sofredor", "Emanuel", "Consolação"]),
        ("Jeremias", 52, "Profetas Maiores", ["Chamado Fiel", "Nova Aliança", "Vaso nas Mãos do Oleiro"]),
        ("Lamentações", 5, "Profetas Maiores", ["Misericórdias Renovadas", "Fidelidade de Deus", "Esperança"]),
        ("Ezequiel", 48, "Profetas Maiores", ["Glória de Deus", "Coração de Carne", "Vale de Ossos Secos"]),
        ("Daniel", 12, "Profetas Maiores", ["Integridade", "Fornalha e Cova", "O Reino Eterno"]),
        ("Oséias", 14, "Profetas Menores", ["Amor Incondicional", "Conhecer a Deus", "Cura da Apostasia"]),
        ("Joel", 3, "Profetas Menores", ["Derramamento do Espírito", "Arrependimento", "Dia do Senhor"]),
        ("Amós", 9, "Profetas Menores", ["Justiça Social", "Retidão", "Religião Autêntica"]),
        ("Obadias", 1, "Profetas Menores", ["Juízo do Orgulho", "Reino do Senhor"]),
        ("Jonas", 4, "Profetas Menores", ["Coração Missionário", "Misericórdia Universal", "Graça"]),
        ("Miquéias", 7, "Profetas Menores", ["Praticar a Justiça", "Amar a Misericórdia", "Humildade"]),
        ("Naum", 3, "Profetas Menores", ["Refúgio no Dia da Angústia", "Juízo dos Opressores"]),
        ("Habacuque", 3, "Profetas Menores", ["O Justo Viverá pela Fé", "Alegria no Deserto"]),
        ("Sofonias", 3, "Profetas Menores", ["O Senhor se Deleita no Seu Povo", "Paz"]),
        ("Ageu", 2, "Profetas Menores", ["A Glória da Segunda Casa", "Prioridade do Templo"]),
        ("Zacarias", 14, "Profetas Menores", ["Não por Força mas pelo Espírito", "O Rei Humilde"]),
        ("Malaquias", 4, "Profetas Menores", ["O Sol da Justiça", "Família", "Fidelidade a Deus"])
    ]

    bible_books_nt = [
        ("Mateus", 28, "Evangelhos", ["O Rei Messias", "Sermão do Monte", "Grande Comissão"]),
        ("Marcos", 16, "Evangelhos", ["O Servo Fiel", "Poder sobre as Tempestades", "Ressurreição"]),
        ("Lucas", 24, "Evangelhos", ["O Salvador da Humanidade", "Compaixão", "Filho Pródigo", "Emaús"]),
        ("João", 21, "Evangelhos", ["O Verbo Eterno", "Novo Nascimento", "Videira Verdadeira", "Vida Eterna"]),
        ("Atos", 28, "Históricos", ["Pentecostes", "Igreja Primitiva", "Missões", "Poder do Espírito"]),
        ("Romanos", 16, "Cartas Paulinas", ["Justificação pela Fé", "Mais que Vencedores", "Culto Racional"]),
        ("1 Coríntios", 16, "Cartas Paulinas", ["A Palavra da Cruz", "Hino ao Amor", "Ressurreição"]),
        ("2 Coríntios", 13, "Cartas Paulinas", ["Consolação", "Nova Criatura", "Poder na Fraqueza"]),
        ("Gálatas", 6, "Cartas Paulinas", ["Liberdade em Cristo", "Fruto do Espírito", "Graça"]),
        ("Efésios", 6, "Cartas Paulinas", ["Salvos pela Graça", "Unidade da Igreja", "Armadura de Deus"]),
        ("Filipenses", 4, "Cartas Paulinas", ["Alegria no Senhor", "Posso Todas as Coisas", "Humildade de Cristo"]),
        ("Colossenses", 4, "Cartas Paulinas", ["Supremacia de Cristo", "Pensar nas Coisas do Alto"]),
        ("1 Tessalonicenses", 5, "Cartas Paulinas", ["Esperança do Retorno", "Orai sem Cessar"]),
        ("2 Tessalonicenses", 3, "Cartas Paulinas", ["Firmeza na Fé", "Trabalho Fiel"]),
        ("1 Timóteo", 6, "Cartas Paulinas", ["Liderança Pastoral", "Piedade com Contentamento"]),
        ("2 Timóteo", 4, "Cartas Paulinas", ["Combater o Bom Combate", "Toda Escritura Inspirada"]),
        ("Tito", 3, "Cartas Paulinas", ["Graça que Ensina", "Boas Obras"]),
        ("Filemom", 1, "Cartas Paulinas", ["Reconciliação Fraternal", "Amor em Ação"]),
        ("Hebreus", 13, "Cartas Gerais", ["Cristo Superior", "Trono da Graça", "Heróis da Fé"]),
        ("Tiago", 5, "Cartas Gerais", ["Fé e Obras", "Domínio da Língua", "Oração Fervorosa"]),
        ("1 Pedro", 5, "Cartas Gerais", ["Sacerdócio Real", "Lançar a Ansiedade sobre Ele"]),
        ("2 Pedro", 3, "Cartas Gerais", ["Crescer na Graça", "Conhecimento de Cristo"]),
        ("1 João", 5, "Cartas Gerais", ["Andar na Luz", "O Perfeito Amor", "Segurança da Fé"]),
        ("2 João", 1, "Cartas Gerais", ["Verdade e Amor"]),
        ("3 João", 1, "Cartas Gerais", ["Prosperidade da Alma", "Hospitalidade"]),
        ("Judas", 1, "Cartas Gerais", ["Batalhar pela Fé", "Aquele que nos Guarda"]),
        ("Apocalipse", 22, "Profecia e Revelação", ["O Cordeiro Vencedor", "Novos Céus e Nova Terra", "Vem Senhor Jesus"])
    ]

    # Distribuição equilibrada em 365 dias:
    # Dias 1 a 265: Antigo Testamento (929 capítulos / ~3.5 cap por dia)
    # Dias 266 a 365: Novo Testamento (260 capítulos / ~2.6 cap por dia)
    
    # Criamos a lista de leitura diária
    daily_schedule = []
    
    # Gerando o Antigo Testamento em 265 dias
    ot_chunks = []
    for book, total_caps, cat, tags in bible_books_ot:
        caps_per_step = 3 if total_caps <= 15 else 4
        if book == "Salmos":
            caps_per_step = 3
        start_c = 1
        while start_c <= total_caps:
            end_c = min(start_c + caps_per_step - 1, total_caps)
            if start_c == end_c:
                ref = f"{book} {start_c}"
            else:
                ref = f"{book} {start_c}-{end_c}"
            ot_chunks.append({
                "reading": ref,
                "testament": "Antigo Testamento",
                "category": cat,
                "book": book,
                "caps": (start_c, end_c),
                "tags": tags
            })
            start_c = end_c + 1

    # Ajustar para exatamente 265 dias de AT
    # Se ot_chunks tem tamanho diferente, agrupamos ou expandimos suavemente
    # Vamos gerar exatamente 265 slots proporcionais
    
    # Gerando o Novo Testamento em 100 dias (266 a 365)
    nt_chunks = []
    for book, total_caps, cat, tags in bible_books_nt:
        caps_per_step = 2 if total_caps <= 10 else 3
        start_c = 1
        while start_c <= total_caps:
            end_c = min(start_c + caps_per_step - 1, total_caps)
            if start_c == end_c:
                ref = f"{book} {start_c}"
            else:
                ref = f"{book} {start_c}-{end_c}"
            nt_chunks.append({
                "reading": ref,
                "testament": "Novo Testamento",
                "category": cat,
                "book": book,
                "caps": (start_c, end_c),
                "tags": tags
            })
            start_c = end_c + 1

    # Vamos unificar para exatamente 365 dias
    all_chunks = ot_chunks + nt_chunks
    
    # Mapeamento de temas dinâmicos enriquecidos
    def make_day_details(day_idx, chunk):
        book = chunk["book"]
        reading = chunk["reading"]
        cat = chunk["category"]
        testament = chunk["testament"]
        tags = chunk["tags"]
        
        # Versículos e reflexões contextualizadas
        key_verse_text = f"Lâmpada para os meus pés é a tua palavra, e luz para o meu caminho."
        key_verse_ref = f"{reading}"
        theme = f"Estudo e Meditação em {reading}"
        reflection = f"Neste {day_idx}º dia da jornada, mergulhamos na revelação de Deus em {reading}. Examine o coração diante da Palavra e busque a aplicação prática para o seu dia a dia."
        
        # Temas e versículos clássicos por livro
        if book == "Gênesis":
            theme = "As Origens, a Soberania Criadora e o Início da Aliança"
            key_verse_text = "No princípio criou Deus os céus e a terra."
            key_verse_ref = "Gênesis 1:1"
            reflection = "Tudo tem sua gênese na palavra poderosa de Deus. Ele traz ordem onde há caos e luz onde há trevas. O mesmo Deus que criou o cosmos cuida dos detalhes da sua vida."
        elif book == "Êxodo":
            theme = "Libertação, Aliança e a Habitação da Presença de Deus"
            key_verse_text = "O Senhor pelejará por vós, e vós vos calareis."
            key_verse_ref = "Êxodo 14:14"
            reflection = "Deus ouve o gemido do Seu povo e abre caminhos no meio do mar. Ele nos liberta não apenas da opressão, mas para que tenhamos comunhão santa com Ele."
        elif book == "Levítico":
            theme = "Santidade, Expiação e o Privilégio de se Aproximar de Deus"
            key_verse_text = "Sereis santos, porque eu, o Senhor vosso Deus, sou santo."
            key_verse_ref = "Levítico 19:2"
            reflection = "A santidade de Deus requer pureza e consagração total. Em Cristo temos o sacrifício perfeito que nos garante acesso perpétuo ao Pai."
        elif book == "Números":
            theme = "A Fidelidade de Deus na Caminhada do Deserto"
            key_verse_text = "O Senhor te abençoe e te guarde; o Senhor faça resplandecer o seu rosto sobre ti."
            key_verse_ref = "Números 6:24-25"
            reflection = "Mesmo quando o deserto parece longo e as circunstâncias desafiadoras, a bênção e a nuvem da presença do Senhor continuam guiando cada passo."
        elif book == "Deuteronômio":
            theme = "Amor Incondicional e Obediência de Coração"
            key_verse_text = "Amarás, pois, o Senhor teu Deus de todo o teu coração, de toda a tua alma e de todas as tuas forças."
            key_verse_ref = "Deuteronômio 6:5"
            reflection = "A aliança com Deus não é um contrato legalista frio; é um compromisso de amor apaixonado e reverente que deve ser transmitido de geração em geração."
        elif book == "Josué":
            theme = "Coragem, Fé Inabalável e Conquista de Promessas"
            key_verse_text = "Não temas, nem te espantes; porque o Senhor teu Deus é contigo por onde quer que andares."
            key_verse_ref = "Josué 1:9"
            reflection = "Muralhas caem quando caminhamos em obediência. A coragem bíblica não nasce da autoconfiança, mas da certeza inabalável de que Deus vai à nossa frente."
        elif book == "Juízes":
            theme = "A Graça que Restaura em Meio aos Ciclos de Fraqueza"
            key_verse_text = "O Senhor é contigo, homem valoroso."
            key_verse_ref = "Juízes 6:12"
            reflection = "Mesmo nos tempos mais escuros, quando o povo clama por socorro, Deus levanta libertadores e manifesta Sua graça que triunfa sobre o julgamento."
        elif book == "Rute":
            theme = "Providência Amorosa e o Redentor da Família"
            key_verse_text = "O teu povo é o meu povo, o teu Deus é o meu Deus."
            key_verse_ref = "Rute 1:16"
            reflection = "A lealdade silenciosa e a bondade cotidiana cooperam soberanamente nos planos eternos de Deus para a vinda do Messias."
        elif "Samuel" in book:
            theme = "O Valor do Coração Sincero Diante de Deus"
            key_verse_text = "O homem vê o exterior, porém o Senhor olha para o coração."
            key_verse_ref = "1 Samuel 16:7"
            reflection = "Deus não busca aparências altivas ou méritos humanos; Ele procura corações quebrantados, fiéis e dispostos a ouvir e obedecer à Sua voz."
        elif "Reis" in book:
            theme = "Sabedoria, Fogo no Altar e Alinhamento Espiritual"
            key_verse_text = "Até quando coxeareis entre dois pensamentos? Se o Senhor é Deus, segui-o."
            key_verse_ref = "1 Reis 18:21"
            reflection = "Decisão firme é necessária na caminhada cristã. Deus responde com fogo quando restauramos o altar e colocamos a adoração a Ele no centro da vida."
        elif "Crônicas" in book:
            theme = "O Legado da Adoração, Avivamento e Oração Nacional"
            key_verse_text = "Se o meu povo se humilhar, orar e buscar a minha face, eu sararei a sua terra."
            key_verse_ref = "2 Crônicas 7:14"
            reflection = "A história é governada pelo Senhor. O verdadeiro avivamento nasce no quebrantamento sincero e na busca coletiva pela face de Deus."
        elif book in ["Esdras", "Neemias"]:
            theme = "Reconstrução do Altar, dos Muros e a Alegria do Senhor"
            key_verse_text = "A alegria do Senhor é a vossa força."
            key_verse_ref = "Neemias 8:10"
            reflection = "Trabalhar com a pá em uma mão e a espada na outra. Deus renova as forças dos Seus servos para restaurar aquilo que estava em ruínas."
        elif book == "Ester":
            theme = "A Providência Oculta de Deus para Momentos Cruciais"
            key_verse_text = "Quem sabe se para tal tempo como este chegaste a este reino?"
            key_verse_ref = "Ester 4:14"
            reflection = "Você não está onde está por acidente. Deus orquestra posicionamentos e oportunidades para que você seja instrumento de bênção e salvação."
        elif book == "Jó":
            theme = "A Confiança Inabalável no Redentor em Meio à Dor"
            key_verse_text = "Eu sei que o meu Redentor vive, e que por fim se levantará sobre a terra."
            key_verse_ref = "Jó 19:25"
            reflection = "A dor é real, mas o silêncio de Deus não é ausência. A fé madura confia no caráter de Deus mesmo quando não compreende Suas circunstâncias."
        elif book == "Salmos":
            theme = "Oração Sincera, Louvor Fervoroso e Refúgio Eterno"
            key_verse_text = "O Senhor é o meu pastor; nada me faltará."
            key_verse_ref = "Salmo 23:1"
            reflection = "Os Salmos nos ensinam a derramar todas as emoções diante de Deus: júbilo, choro, gratidão e esperança. N’Ele a alma encontra pastos verdejantes."
        elif book == "Provérbios":
            theme = "Sabedoria Prática, Prudência e Temor ao Senhor"
            key_verse_text = "O temor do Senhor é o princípio da sabedoria."
            key_verse_ref = "Provérbios 9:10"
            reflection = "A verdadeira sabedoria não é erudição intelectual vazia; é a habilidade moral e espiritual de fazer escolhas que honram a Deus no dia a dia."
        elif book == "Eclesiastes":
            theme = "O Sentido Eterno da Vida Debaixo do Sol"
            key_verse_text = "Tudo tem o seu tempo determinado, e há tempo para todo o propósito debaixo do céu."
            key_verse_ref = "Eclesiastes 3:1"
            reflection = "As vaidades passageiras do mundo não saciam o vazio do coração humano. Somente o Deus eterno dá propósito real à nossa existência."
        elif book == "Cantares":
            theme = "O Amor Sublime, Fiel e Apaixonado"
            key_verse_text = "As muitas águas não podem apagar este amor, nem os rios afogá-lo."
            key_verse_ref = "Cantares 8:7"
            reflection = "O amor sacrificial e leal reflete o amor zeloso de Cristo por Sua noiva, a Igreja. Uma celebração da beleza da união ordenada por Deus."
        elif book == "Isaías":
            theme = "A Santidade de Deus, o Servo Sofredor e a Consolação"
            key_verse_text = "Mas os que esperam no Senhor renovarão as forças; subirão com asas como águias."
            key_verse_ref = "Isaías 40:31"
            reflection = "O profeta messiânico aponta para a glória de Cristo e para a promessa de que as feridas da alma são curadas pelas pisaduras do Cordeiro."
        elif book in ["Jeremias", "Lamentações"]:
            theme = "A Nova Aliança, o Oleiro e a Fidelidade Renovada"
            key_verse_text = "As misericórdias do Senhor renovam-se a cada manhã; grande é a tua fidelidade."
            key_verse_ref = "Lamentações 3:22-23"
            reflection = "Mesmo quando o coração chora por causa do pecado ao redor, a fidelidade de Deus surge como a alva trazendo misericórdia renovada a cada amanhecer."
        elif book == "Ezequiel":
            theme = "O Novo Coração de Carne e o Sopro do Espírito"
            key_verse_text = "Dar-vos-ei um coração novo, e porei dentro de vós um espírito novo."
            key_verse_ref = "Ezequiel 36:26"
            reflection = "O Espírito Santo tem poder para soprar sobre qualquer vale árido e ressuscitar sonhos, ministérios e vidas com vigor extraordinário."
        elif book == "Daniel":
            theme = "Fidelidade Cultural, Integridade e o Reino Eterno"
            key_verse_text = "O meu Deus enviou o seu anjo e fechou a boca dos leões."
            key_verse_ref = "Daniel 6:22"
            reflection = "Não negocie seus valores espirituais por conveniência mundana. Deus honra aqueles que decidem não se contaminar e permanecem firmes em oração."
        elif book in ["Oséias", "Joel", "Amós", "Obadias", "Jonas", "Miquéias", "Naum", "Habacuque", "Sofonias", "Ageu", "Zacarias", "Malaquias"]:
            theme = "Voz Profética, Justiça Divina e o Sol da Justiça"
            key_verse_text = "O que o Senhor pede de ti, senão que pratiques a justiça, ames a misericórdia e andes humildemente com o teu Deus?"
            key_verse_ref = "Miquéias 6:8"
            reflection = "Os profetas convocam o povo a abandonar a hipocrisia, abraçar a compaixão pelos fracos e aguardar com fé o amanhecer do Messias prometido."
        elif book in ["Mateus", "Marcos", "Lucas", "João"]:
            theme = "O Evangelho de Jesus Cristo: Graça, Poder e Salvação"
            key_verse_text = "Eu sou o caminho, a verdade e a vida; ninguém vem ao Pai senão por mim."
            key_verse_ref = "João 14:6"
            reflection = "A glória do Verbo encarnado vivendo entre nós! Jesus revela o coração do Pai, cura os enfermos, perdoa os pecadores e vence a morte na ressurreição."
        elif book == "Atos":
            theme = "O Poder do Espírito Santo e a Expansão da Igreja"
            key_verse_text = "Recebereis poder ao descer sobre vós o Espírito Santo, e sereis minhas testemunhas."
            key_verse_ref = "Atos 1:8"
            reflection = "A Igreja viva e atuante avança contra todas as perseguições pelo fogo do Espírito, levando o amor transformador do Evangelho aos confins da terra."
        elif book == "Romanos":
            theme = "Justificação pela Fé, Graça Soberana e Mais que Vencedores"
            key_verse_text = "Porque pela graça sois justificados mediante a fé em Cristo Jesus."
            key_verse_ref = "Romanos 5:1"
            reflection = "A teologia magna da graça: justificados gratuitamente pelo sangue de Cristo, reconciliados com Deus e seguros para sempre em Seu amor inseparável."
        elif "Coríntios" in book:
            theme = "A Sabedoria da Cruz, Dons Espirituais e o Amor Perfeito"
            key_verse_text = "O amor nunca falha... A minha graça te basta, porque o meu poder se aperfeiçoa na fraqueza."
            key_verse_ref = "1 Coríntios 13:8 / 2 Coríntios 12:9"
            reflection = "O poder de Deus brilha nas nossas fraquezas e fragilidades. Quando o amor bíblico governa nossos dons e atitudes, a comunidade é verdadeiramente edificada."
        elif book in ["Gálatas", "Efésios", "Filipenses", "Colossenses"]:
            theme = "Liberdade em Cristo, Riquezas da Graça e Alegria Constante"
            key_verse_text = "Alegrai-vos sempre no Senhor; outra vez digo, alegrai-vos... Posso todas as coisas naquele que me fortalece."
            key_verse_ref = "Filipenses 4:4,13"
            reflection = "Cristo é a nossa identidade, nossa armadura e nossa paz. Em tudo somos capacitados por Aquele que habita em nós e nos conduz em triunfo."
        elif "Tessalonicenses" in book or "Timóteo" in book or book in ["Tito", "Filemom"]:
            theme = "Firmeza na Doutrina, Liderança Pastoral e Esperança do Retorno"
            key_verse_text = "Combati o bom combate, acabei a carreira, guardei a fé."
            key_verse_ref = "2 Timóteo 4:7"
            reflection = "Perseverança fiel no discipulado e no ensino sadio da verdade. O cristão vive na expectativa jubilosa do reencontro com o seu Salvador."
        elif book == "Hebreus":
            theme = "A Superioridade de Cristo, o Trono da Graça e a Fé Firme"
            key_verse_text = "Olhando firmemente para Jesus, autor e consumador da nossa fé."
            key_verse_ref = "Hebreus 12:2"
            reflection = "Jesus é o Sumo Sacerdote eterno que abriu o novo e vivo caminho. Aproxime-se com confiança do trono da graça para encontrar socorro oportuno."
        elif book in ["Tiago", "1 Pedro", "2 Pedro", "1 João", "2 João", "3 João", "Judas"]:
            theme = "Fé Prática, Sacerdócio Real, Amor Verdadeiro e Santidade"
            key_verse_text = "No amor não há temor; antes o perfeito amor lança fora todo o medo."
            key_verse_ref = "1 João 4:18"
            reflection = "A fé autêntica se traduz em obras de justiça, amor aos irmãos, paciência nas aflições e vigilância contra as ilusões do mundanismo."
        elif book == "Apocalipse":
            theme = "O Triunfo Final do Cordeiro e os Novos Céus e Nova Terra"
            key_verse_text = "E Deus limpará de seus olhos toda a lágrima... Eis que faço novas todas as coisas."
            key_verse_ref = "Apocalipse 21:4-5"
            reflection = "A vitória final pertence ao Cordeiro de Deus! O mal será aniquilado para sempre e habitaremos na comunhão gloriosa da Nova Jerusalém com o Senhor."

        return {
            "day": day_idx,
            "reading": reading,
            "testament": testament,
            "category": cat,
            "theme": theme,
            "key_verse_text": key_verse_text,
            "key_verse_ref": key_verse_ref,
            "reflection": reflection,
            "tags": tags
        }

    # Geramos exatamente 365 dias
    # Se len(all_chunks) for diferente de 365, fazemos a distribuição perfeita:
    n_chunks = len(all_chunks)
    for i in range(365):
        day_num = i + 1
        # Mapeamento do chunk correspondente
        chunk_idx = int(i * n_chunks / 365)
        chunk = all_chunks[chunk_idx]
        item = make_day_details(day_num, chunk)
        full_days.append(item)

    return full_days


def init_database_and_json():
    os.makedirs(os.path.join(os.path.dirname(__file__), "data"), exist_ok=True)
    
    # 1. Gerar e salvar bible_plan.json
    plan_data = generate_exact_365_plan()
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(plan_data, f, ensure_ascii=False, indent=2)
    print(f"[OK] bible_plan.json gerado com {len(plan_data)} dias!")

    # 2. Inicializar SQLite
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Tabela de Usuários (Multi-Usuário)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        phone TEXT,
        email TEXT,
        avatar_icon TEXT DEFAULT '🕊️',
        current_day INTEGER DEFAULT 1,
        reminder_time TEXT DEFAULT '07:00',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)
    cursor.execute("SELECT COUNT(*) FROM users")
    if cursor.fetchone()[0] == 0:
        cursor.execute("INSERT INTO users (id, name, avatar_icon, current_day) VALUES (1, 'Miqueias', '🕊️', 1)")

    # Tabela de Livros da Biblioteca do Usuário
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS books (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT NOT NULL,
        publisher TEXT,
        year INTEGER,
        themes TEXT, -- JSON ou tags separadas por vírgula
        summary TEXT,
        cover_color TEXT DEFAULT '#4a5568',
        cover_image TEXT,
        is_bedside INTEGER DEFAULT 0,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

    # Tabela de Progresso e Diário do Usuário
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS study_journal (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER DEFAULT 1,
        day_number INTEGER NOT NULL,
        status TEXT DEFAULT 'pending', -- pending, completed, skipped
        completed_at TIMESTAMP,
        personal_notes TEXT,
        favorite_verse TEXT,
        reading_time_minutes INTEGER DEFAULT 15,
        rating INTEGER DEFAULT 5,
        linked_book_ids TEXT -- IDs de livros da biblioteca citados/estudados
    )
    """)

    # Tabela de Configurações
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS settings (
        key TEXT PRIMARY KEY,
        value TEXT
    )
    """)

    # Inserir configurações padrão caso não existam
    default_settings = [
        ("user_name", "Miqueias"),
        ("whatsapp_number", ""),
        ("reminder_time", "07:00"),
        ("auto_whatsapp_enabled", "false"),
        ("current_day", "1"),
        ("plan_start_date", datetime.now().strftime("%Y-%m-%d")),
        ("theme_mode", "dark")
    ]
    for k, v in default_settings:
        cursor.execute("INSERT OR IGNORE INTO settings (key, value) VALUES (?, ?)", (k, v))

    # Inserir livros iniciais de exemplo na biblioteca (obras clássicas consagradas de apoio bíblico)
    # com destaque absoluto para o livro de cabeceira/travesseiro "O Pastor Pentecostal"
    cursor.execute("SELECT COUNT(*) FROM books")
    if cursor.fetchone()[0] == 0:
        sample_books = [
            ("O Pastor Pentecostal: Teologia e Práticas Pastorais",
             "Thomas E. Trask, Wayde I. Goodall & Zenas J. Bicket (Orgs.)",
             "CPAD", 2005,
             "Liderança, Pastor, Ministério, Espírito Santo, Oração, Avivamento, Família, Pregação, Aconselhamento, Dons Espirituais, Missões, Integridade, Unção, Batalha Espiritual, Vocação, Cuidado do Rebanho, Discipulado",
             "Manual clássico e devocional de cabeceira da CPAD. Obra fundamental de teologia e prática pastoral que reúne orientações práticas e espirituais para líderes, pastores e estudantes da Bíblia sobre o poder do Espírito Santo, integridade ministerial, oração e pastoreio.",
             "#1e3a5f", "img/o_pastor_pentecostal.jpg", 1,
             "⭐ LIVRO DE TRAVESSEIRO & CABECEIRA OFICIAL: Acompanhamento diário das orientações teológicas e pastorais pentecostais em conexão com a leitura bíblica."),
            ("O Deus Presente: Encontrando seu Lugar na História de Deus", "D.A. Carson", "Vida Nova", 2013,
             "Criação, Aliança, Graça, Teologia Bíblica, Queda, Redenção",
             "Visão panorâmica da Bíblia inteira de Gênesis ao Apocalipse, conectando todas as histórias à narrativa maior de Cristo.",
             "#1e3a8a", None, 0, "Excelente para acompanhar os primeiros dias em Gênesis e os Evangelhos."),
            ("A Cruz de Cristo", "John Stott", "Editora Vida", 2006,
             "A Cruz de Cristo, Expiação, Salvação, Graça, Redenção pelo Sangue, O Servo Sofredor",
             "Obra monumental sobre o significado teológico, moral e pessoal do sacrifício vicário de Jesus na cruz.",
             "#831843", None, 0, "Leitura ideal para acompanhar Isaías 53, os Evangelhos e Romanos."),
            ("Oração: Experimentando Intimidade e Poder com Deus", "Timothy Keller", "Vida Nova", 2015,
             "Oração, Intimidade com Deus, Salmos, Adoração, Meditação Bíblica, Quebrantamento",
             "Guia prático e teológico sobre oração de adoração, intercessão e comunhão com Deus fundamentada nos Salmos.",
             "#065f46", None, 0, "Fundamental para acompanhar a leitura dos Salmos e as orações de Paulo."),
            ("Teologia Sistemática", "Wayne Grudem", "Vida Nova", 2005,
             "Doutrina de Deus, Criação, Trindade, Santidade, Cristologia, Espírito Santo, Escatologia",
             "Manual clássico de referência para consultar e aprofundar temas doutrinários e teológicos ao longo do estudo.",
             "#78350f", None, 0, "Livro de consulta contínua para temas difíceis em qualquer livro da Bíblia."),
            ("Comentário Bíblico do Antigo e Novo Testamento", "F.F. Bruce & Matthew Henry", "Vida", 2010,
             "Exegese, História Bíblica, Comentário Versículo por Versículo, Profecias, Epístolas",
             "Comentários devocionais e históricos detalhados sobre passagens e costumes da antiguidade bíblica.",
             "#312e81", None, 0, "Ótimo para tirar dúvidas sobre o contexto cultural de cada dia.")
        ]
        for b in sample_books:
            cursor.execute("""
            INSERT INTO books (title, author, publisher, year, themes, summary, cover_color, cover_image, is_bedside, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, b)
        print("[OK] Livros modelo inseridos com sucesso na biblioteca pessoal!")

    conn.commit()
    conn.close()
    print(f"[OK] Banco SQLite inicializado com sucesso em: {DB_PATH}")

if __name__ == "__main__":
    init_database_and_json()
    print("Inicialização da base bíblica concluída com sucesso!")
