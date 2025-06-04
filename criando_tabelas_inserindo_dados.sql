-- =========== CRIAÇÃO DAS TABELAS (LDD) ===========

-- Tabela GrupoArmado
CREATE TABLE GrupoArmado (
    CodigoG SERIAL PRIMARY KEY,
    NomeGrupo VARCHAR(100) NOT NULL UNIQUE,
    NumBaixasG INT DEFAULT 0
);

-- Tabela LiderPolitico
CREATE TABLE LiderPolitico (
    NomeL VARCHAR(100) PRIMARY KEY,
    CodigoG INT,
    Apoios TEXT,
    FOREIGN KEY (CodigoG) REFERENCES GrupoArmado(CodigoG)
);

-- Tabela Divisao
CREATE TABLE Divisao (
    NroDivisao SERIAL,
    CodigoG INT,
    NumBaixasD INT DEFAULT 0,
    Barcos INT,
    Tanques INT,
    Avioes INT,
    Homens INT,
    PRIMARY KEY (NroDivisao, CodigoG),
    FOREIGN KEY (CodigoG) REFERENCES GrupoArmado(CodigoG)
);

-- Tabela ChefeMilitar
CREATE TABLE ChefeMilitar (
    codigoChef SERIAL PRIMARY KEY,
    Faixa VARCHAR(50),
    NroDivisao INT,
    CodigoG INT,
    NomeL VARCHAR(100),
    FOREIGN KEY (NroDivisao, CodigoG) REFERENCES Divisao(NroDivisao, CodigoG),
    FOREIGN KEY (NomeL) REFERENCES LiderPolitico(NomeL)
);

-- Tabela Conflito
CREATE TABLE Conflito (
    CodConflito SERIAL PRIMARY KEY,
    Nome VARCHAR(100) NOT NULL,
    NumFeridos INT,
    NumMortos INT,
    TipoConf VARCHAR(50) -- Pode ser 'Territorial', 'Religioso', 'Economico', 'Racial'
);

-- Tabela ConflitoPais
CREATE TABLE ConflitoPais (
    CodConflito INT,
    Pais VARCHAR(100),
    PRIMARY KEY (CodConflito, Pais),
    FOREIGN KEY (CodConflito) REFERENCES Conflito(CodConflito)
);

-- especialização de Conflitos
-- Tabelas para os tipos de conflitos (Hierarquia)
CREATE TABLE Territorial (
    CodConflito INT PRIMARY KEY,
    Regiao VARCHAR(100),
    FOREIGN KEY (CodConflito) REFERENCES Conflito(CodConflito)
);

CREATE TABLE Religioso (
    CodConflito INT PRIMARY KEY,
    Religiao VARCHAR(100),
    FOREIGN KEY (CodConflito) REFERENCES Conflito(CodConflito)
);

CREATE TABLE Economico (
    CodConflito INT PRIMARY KEY,
    MatPrima VARCHAR(100),
    FOREIGN KEY (CodConflito) REFERENCES Conflito(CodConflito)
);

CREATE TABLE Racial (
    CodConflito INT PRIMARY KEY,
    Etnia VARCHAR(100),
    FOREIGN KEY (CodConflito) REFERENCES Conflito(CodConflito)
);


-- Tabela de Participação de Grupos Armados em Conflitos (EntPart)
CREATE TABLE EntPart (
    IdEntPart SERIAL PRIMARY KEY,
    CodigoG INT,
    CodConflito INT,
    DEGrupo DATE, -- Data de entrada
    DSGrupo DATE, -- Data de saída
    FOREIGN KEY (CodigoG) REFERENCES GrupoArmado(CodigoG),
    FOREIGN KEY (CodConflito) REFERENCES Conflito(CodConflito)
);


-- Tabela OrganizacaoM
CREATE TABLE OrganizacaoM (
    CodigoOrg SERIAL PRIMARY KEY,
    NomeOrg VARCHAR(100) NOT NULL,
    Tipo VARCHAR(50) NOT NULL CHECK (Tipo IN ('governamental', 'não governamental', 'internacional')),
    OrgLider INT REFERENCES OrganizacaoM(CodigoOrg)
);


-- Tabela de Mediação de Organizações em Conflitos (EntradMed)
CREATE TABLE EntradMed (
    IdEntMed SERIAL PRIMARY KEY,
    CodigoOrg INT,
    CodConflito INT,
    DEMedia DATE, -- Data de entrada
    DSMedia DATE, -- Data de saída
    NumPessoas INT,
    TipoAjuda VARCHAR(50) CHECK (TipoAjuda IN ('médica', 'diplomática', 'presencial')),
    FOREIGN KEY (CodigoOrg) REFERENCES OrganizacaoM(CodigoOrg),
    FOREIGN KEY (CodConflito) REFERENCES Conflito(CodConflito)
);

-- Tabela Dialoga
CREATE TABLE Dialoga (
    IdDial SERIAL PRIMARY KEY,
    NomeL VARCHAR(100),
    CodigoOrg INT,
    FOREIGN KEY (NomeL) REFERENCES LiderPolitico(NomeL),
    FOREIGN KEY (CodigoOrg) REFERENCES OrganizacaoM(CodigoOrg) ON DELETE SET NULL
);

-- Tabela Traficante
CREATE TABLE Traficante (
    NomeTraf VARCHAR(100) PRIMARY KEY
);

-- Tabela TipoArma
CREATE TABLE TipoArma (
    NomeArma VARCHAR(100) PRIMARY KEY,
    Indicador INT -- Capacidade destrutiva
);

-- Tabela PodeFornecer (relaciona Traficante e TipoArma)
CREATE TABLE PodeFornecer (
    IdPodeF SERIAL PRIMARY KEY,
    NomeTraf VARCHAR(100),
    NomeArma VARCHAR(100),
    Quantidade INT,
    FOREIGN KEY (NomeTraf) REFERENCES Traficante(NomeTraf),
    FOREIGN KEY (NomeArma) REFERENCES TipoArma(NomeArma)
);

-- Tabela Fornece (relaciona Traficante, TipoArma e GrupoArmado)
CREATE TABLE Fornece (
    IdFornece SERIAL PRIMARY KEY,
    CodigoG INT,
    NomeArma VARCHAR(100),
    NomeTraf VARCHAR(100),
    NumArmas INT,
    FOREIGN KEY (CodigoG) REFERENCES GrupoArmado(CodigoG),
    FOREIGN KEY (NomeArma) REFERENCES TipoArma(NomeArma),
    FOREIGN KEY (NomeTraf) REFERENCES Traficante(NomeTraf)
);


-- =========== POPULANDO AS TABELAS ===========

-- Inserindo Grupos Armados
INSERT INTO GrupoArmado (NomeGrupo) VALUES
('Exército de Libertação Nacional'),
('Forças Armadas Revolucionárias'),
('Guarda Republicana'),
('Milícia do Povo'),
('Aliança Rebelde'),
('Império Galáctico'),
('Legião da Sombra'),
('Coalizão do Norte');


INSERT INTO LiderPolitico (NomeL, CodigoG, Apoios) VALUES
('General Aladeen', 3, 'Apoio de nações vizinhas e conglomerados de petróleo.'),
('Comandante Cobra', 2, 'Financiado por corporações internacionais de armas.'),
('Presidente Snow', 1, 'Apoiado pela elite rica e pelo aparato estatal.'),
('Líder Koba', 4, 'Suporte de facções separatistas e contrabandistas.'),
('Mon Mothma', 5, 'Apoiada por senadores dissidentes e sistemas estelares oprimidos.'),
('Imperador Palpatine', 6, 'Controle total do Senado Galáctico e da frota imperial.'),
('Lorde das Sombras', 7, 'Poder derivado de fontes arcanas e cultos secretos.'),
('Rei do Norte', 8, 'Lealdade dos clãs das montanhas e cidades-estado do norte.');


-- Inserindo Divisões dos Grupos Armados
INSERT INTO Divisao (CodigoG, NumBaixasD, Barcos, Tanques, Avioes, Homens) VALUES
(1, 120, 10, 50, 20, 5000),         -- Exército de Libertação Nacional
(1, 250, 5, 80, 15, 7000),          -- Exército de Libertação Nacional
(2, 500, 0, 120, 30, 10000),        -- Forças Armadas Revolucionárias
(3, 80, 30, 150, 50, 12000),        -- Guarda Republicana
(4, 300, 2, 40, 5, 4500),           -- Milícia do Povo
(5, 350, 15, 30, 150, 8000),        -- Aliança Rebelde
(6, 1500, 500, 2000, 1000, 50000),  -- Império Galáctico
(6, 1200, 400, 1500, 800, 45000),   -- Império Galáctico
(7, 400, 5, 100, 10, 6000),         -- Legião da Sombra
(8, 200, 20, 150, 5, 9000);         -- Coalizão do Norte


-- Inserindo Chefes Militares
INSERT INTO ChefeMilitar (Faixa, NroDivisao, CodigoG, NomeL) VALUES
('Coronel', 1, 1, 'Presidente Snow'),
('Major', 2, 1, 'Presidente Snow'),
('General de Brigada', 3, 2, 'Comandante Cobra'),
('Marechal de Campo', 4, 3, 'General Aladeen'),
('Capitão', 5, 4, 'Líder Koba'),
('Almirante Ackbar', 6, 5, 'Mon Mothma'),
('Darth Vader', 7, 6, 'Imperador Palpatine'),
('General Veers', 8, 6, 'Imperador Palpatine'),
('Mestre Assassino', 9, 7, 'Lorde das Sombras'),
('Comandante Bárbaro', 10, 8, 'Rei do Norte');


-- Inserindo Conflitos
INSERT INTO Conflito (Nome, NumFeridos, NumMortos, TipoConf) VALUES
('Guerra do Deserto', 5000, 2000, 'Economico'),
('Insurreição da Primavera', 12000, 4500, 'Territorial'),
('Cruzada Santa do Norte', 8000, 3200, 'Religioso'),
('Guerra de Segregação', 20000, 9000, 'Racial'),
('Batalha pela Água', 3000, 1000, 'Economico'),
('Guerra Civil Galáctica', 1500000, 700000, 'Territorial'),
('A Longa Noite', 50000, 25000, 'Racial'),
('Guerra das Especiarias', 25000, 8000, 'Economico');


-- Detalhando tipos de conflitos
INSERT INTO Economico (CodConflito, MatPrima) VALUES
(1, 'Petróleo'),
(5, 'Água Potável'),
(8, 'Especiaria Melange');

INSERT INTO Territorial (CodConflito, Regiao) VALUES
(2, 'Província do Norte'),
(6, 'Borda Exterior da Galáxia');

INSERT INTO Religioso (CodConflito, Religiao) VALUES
(3, 'Fé do Solstício');

INSERT INTO Racial (CodConflito, Etnia) VALUES
(4, 'Povo do Vale'),
(7, 'Caminhantes Brancos');


-- Inserindo países nos conflitos
INSERT INTO ConflitoPais (CodConflito, Pais) VALUES
(1, 'Brasil'),
(1, 'Venezuela'),
(2, 'Siria'),
(2, 'Líbano'),
(3, 'Estados Unidos'),
(3, 'Canadá'),
(4, 'África do Sul'),
(4, 'Namíbia'),
(5, 'Egito'),
(5, 'Sudão'),
(6, 'Estados Unidos'),
(6, 'Reino Unido'),
(7, 'Irlanda'),
(8, 'Afeganistão'),
(8, 'Paquistão');


-- Inserindo Participação dos Grupos nos Conflitos
INSERT INTO EntPart (CodigoG, CodConflito, DEGrupo, DSGrupo) VALUES
(1, 2, '2023-01-15', NULL),
(2, 2, '2023-01-20', NULL),
(3, 1, '2022-05-10', '2024-08-20'),
(4, 4, '2021-11-01', NULL),
(3, 3, '2023-03-12', NULL),
(5, 6, '2005-05-19', '2010-10-20'),
(6, 6, '2005-05-19', '2010-10-20'),
(7, 7, '2018-01-01', NULL),
(8, 7, '2018-01-01', NULL),
(1, 8, '2024-01-01', NULL);

-- Inserindo Organizações Mediadoras
INSERT INTO OrganizacaoM (NomeOrg, Tipo, OrgLider) VALUES
('Cruz Vermelha Internacional', 'não governamental', NULL),
('Nações Unidas', 'internacional', NULL),
('Médicos Sem Fronteiras', 'não governamental', NULL),
('Ordem Jedi', 'não governamental', NULL),
('Guilda Espacial', 'governamental', NULL);


-- Inserindo Mediação das Organizações nos Conflitos
INSERT INTO EntradMed (CodigoOrg, CodConflito, DEMedia, DSMedia, NumPessoas, TipoAjuda) VALUES
(1, 2, '2023-02-01', NULL, 50, 'médica'),
(2, 2, '2023-03-10', NULL, 25, 'diplomática'),
(3, 4, '2022-01-15', NULL, 80, 'médica'),
(2, 1, '2022-06-01', '2024-07-30', 40, 'presencial'),
(4, 6, '2006-01-01', '2006-05-01', 5, 'diplomática'),
(5, 8, '2024-02-10', NULL, 150, 'presencial'),
(1, 7, '2018-06-20', NULL, 30, 'médica');

-- Inserindo Diálogos
INSERT INTO Dialoga (NomeL, CodigoOrg) VALUES
('Presidente Snow', 2),
('General Aladeen', 1),
('Líder Koba', 3),
('Mon Mothma', 4),
('Imperador Palpatine', 5),
('Rei do Norte', 1);

-- Inserindo Traficantes
INSERT INTO Traficante (NomeTraf) VALUES
('Viktor Bout'),
('Adnan Khashoggi'),
('Lord of War'),
('Hondo Ohnaka'),
('A Baronesa');

-- Inserindo Tipos de Armas
INSERT INTO TipoArma (NomeArma, Indicador) VALUES
('Barret M82', 9),
('M200 Intervention', 10),
('AK-47', 7),
('RPG-7', 8),
('Rifle Blaster E-11', 6),
('Sabre de Luz', 10),
('Canhão de Íons', 8);

-- Inserindo o que cada traficante pode fornecer
INSERT INTO PodeFornecer (NomeTraf, NomeArma, Quantidade) VALUES
('Viktor Bout', 'AK-47', 10000),
('Viktor Bout', 'RPG-7', 5000),
('Adnan Khashoggi', 'Barret M82', 500),
('Lord of War', 'M200 Intervention', 200),
('Lord of War', 'AK-47', 20000),
('Hondo Ohnaka', 'Rifle Blaster E-11', 5000),
('A Baronesa', 'Canhão de Íons', 200),
('A Baronesa', 'Barret M82', 300),
('Viktor Bout', 'M200 Intervention', 150);

-- Inserindo fornecimentos para grupos armados
INSERT INTO Fornece (CodigoG, NomeArma, NomeTraf, NumArmas) VALUES
(2, 'AK-47', 'Viktor Bout', 2000),
(2, 'Barret M82', 'Adnan Khashoggi', 100),
(4, 'RPG-7', 'Viktor Bout', 500),
(3, 'M200 Intervention', 'Lord of War', 50),
(1, 'AK-47', 'Lord of War', 3000),
(5, 'Rifle Blaster E-11', 'Hondo Ohnaka', 1500),
(6, 'Rifle Blaster E-11', 'Hondo Ohnaka', 4000),
(7, 'Barret M82', 'A Baronesa', 50),
(8, 'Canhão de Íons', 'A Baronesa', 10),
(2, 'M200 Intervention', 'Viktor Bout', 20);