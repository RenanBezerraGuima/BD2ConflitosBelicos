-- =========== CRIAÇÃO DAS TABELAS (LDD) ===========
-- Tabela GrupoArmado
DROP TABLE IF EXISTS GrupoArmado CASCADE;

CREATE TABLE IF NOT EXISTS GrupoArmado (
    CodigoG SERIAL PRIMARY KEY,
    NomeGrupo VARCHAR(100) NOT NULL UNIQUE,
    NumBaixasG INT DEFAULT 0
);

-- Tabela LiderPolitico
DROP TABLE IF EXISTS LiderPolitico CASCADE;

CREATE TABLE IF NOT EXISTS LiderPolitico (
    NomeL VARCHAR(100) PRIMARY KEY,
    CodigoG INT,
    Apoios TEXT,
    FOREIGN KEY (CodigoG) REFERENCES GrupoArmado (CodigoG)
);

-- Tabela Divisao
DROP TABLE IF EXISTS Divisao CASCADE;

CREATE TABLE IF NOT EXISTS Divisao (
    NroDivisao INT,
    CodigoG INT,
    NumBaixasD INT DEFAULT 0,
    Barcos INT,
    Tanques INT,
    Avioes INT,
    Homens INT,
    PRIMARY KEY (NroDivisao, CodigoG),
    FOREIGN KEY (CodigoG) REFERENCES GrupoArmado (CodigoG)
);

-- Tabela ChefeMilitar
DROP TABLE IF EXISTS ChefeMilitar CASCADE;

CREATE TABLE IF NOT EXISTS ChefeMilitar (
    codigoChef SERIAL PRIMARY KEY,
    Faixa VARCHAR(50),
    NroDivisao INT,
    CodigoG INT,
    NomeL VARCHAR(100),
    FOREIGN KEY (NroDivisao, CodigoG) REFERENCES Divisao (NroDivisao, CodigoG),
    FOREIGN KEY (NomeL) REFERENCES LiderPolitico (NomeL)
);

-- Tabela Conflito
DROP TABLE IF EXISTS Conflito CASCADE;

CREATE TABLE IF NOT EXISTS Conflito (
    CodConflito SERIAL PRIMARY KEY,
    Nome VARCHAR(100) NOT NULL,
    NumFeridos INT,
    NumMortos INT,
    TipoConf VARCHAR(50) -- Pode ser 'Territorial', 'Religioso', 'Economico', 'Racial'
);

-- Tabela ConflitoPais
DROP TABLE IF EXISTS ConflitoPais CASCADE;

CREATE TABLE IF NOT EXISTS ConflitoPais (
    CodConflito INT,
    Pais VARCHAR(100),
    PRIMARY KEY (CodConflito, Pais),
    FOREIGN KEY (CodConflito) REFERENCES Conflito (CodConflito)
);

-- Tabelas para os tipos de conflitos (Hierarquia)
DROP TABLE IF EXISTS Territorial CASCADE;

CREATE TABLE IF NOT EXISTS Territorial (
    CodConflito INT PRIMARY KEY,
    Regiao VARCHAR(100),
    FOREIGN KEY (CodConflito) REFERENCES Conflito (CodConflito)
);

DROP TABLE IF EXISTS Religioso CASCADE;

CREATE TABLE IF NOT EXISTS Religioso (
    CodConflito INT PRIMARY KEY,
    Religiao VARCHAR(100),
    FOREIGN KEY (CodConflito) REFERENCES Conflito (CodConflito)
);

DROP TABLE IF EXISTS Economico CASCADE;

CREATE TABLE IF NOT EXISTS Economico (
    CodConflito INT PRIMARY KEY,
    MatPrima VARCHAR(100),
    FOREIGN KEY (CodConflito) REFERENCES Conflito (CodConflito)
);

DROP TABLE IF EXISTS Racial CASCADE;

CREATE TABLE IF NOT EXISTS Racial (
    CodConflito INT PRIMARY KEY,
    Etnia VARCHAR(100),
    FOREIGN KEY (CodConflito) REFERENCES Conflito (CodConflito)
);

-- Tabela de Participação de Grupos Armados em Conflitos (EntPart)
DROP TABLE IF EXISTS EntPart CASCADE;

CREATE TABLE IF NOT EXISTS EntPart (
    IdEntPart SERIAL PRIMARY KEY,
    CodigoG INT,
    CodConflito INT,
    DEGrupo DATE, -- Data de entrada
    DSGrupo DATE, -- Data de saída
    FOREIGN KEY (CodigoG) REFERENCES GrupoArmado (CodigoG),
    FOREIGN KEY (CodConflito) REFERENCES Conflito (CodConflito)
);

-- Tabela OrganizacaoM
DROP TABLE IF EXISTS OrganizacaoM CASCADE;

CREATE TABLE IF NOT EXISTS OrganizacaoM (
    CodigoOrg SERIAL PRIMARY KEY,
    NomeOrg VARCHAR(100) NOT NULL,
    Tipo VARCHAR(50) NOT NULL CHECK (
        Tipo IN (
            'governamental',
            'não governamental',
            'internacional'
        )
    ),
    OrgLider INT REFERENCES OrganizacaoM (CodigoOrg)
);

-- Tabela de Mediação de Organizações em Conflitos (EntradMed)
DROP TABLE IF EXISTS EntradMed CASCADE;

CREATE TABLE IF NOT EXISTS EntradMed (
    IdEntMed SERIAL PRIMARY KEY,
    CodigoOrg INT,
    CodConflito INT,
    DEMedia DATE, -- Data de entrada
    DSMedia DATE, -- Data de saída
    NumPessoas INT,
    TipoAjuda VARCHAR(50) CHECK (
        TipoAjuda IN ('médica', 'diplomática', 'presencial')
    ),
    FOREIGN KEY (CodigoOrg) REFERENCES OrganizacaoM (CodigoOrg),
    FOREIGN KEY (CodConflito) REFERENCES Conflito (CodConflito)
);

-- Tabela Dialoga
DROP TABLE IF EXISTS Dialoga CASCADE;

CREATE TABLE IF NOT EXISTS Dialoga (
    IdDial SERIAL PRIMARY KEY,
    NomeL VARCHAR(100),
    CodigoOrg INT,
    FOREIGN KEY (NomeL) REFERENCES LiderPolitico (NomeL),
    FOREIGN KEY (CodigoOrg) REFERENCES OrganizacaoM (CodigoOrg) ON DELETE SET NULL
);

-- Tabela Traficante
DROP TABLE IF EXISTS Traficante CASCADE;

CREATE TABLE IF NOT EXISTS Traficante (NomeTraf VARCHAR(100) PRIMARY KEY);

-- Tabela TipoArma
DROP TABLE IF EXISTS TipoArma CASCADE;

CREATE TABLE IF NOT EXISTS TipoArma (
    NomeArma VARCHAR(100) PRIMARY KEY,
    Indicador INT -- Capacidade destrutiva
);

-- Tabela PodeFornecer (relaciona Traficante e TipoArma)
DROP TABLE IF EXISTS PodeFornecer CASCADE;

CREATE TABLE IF NOT EXISTS PodeFornecer (
    IdPodeF SERIAL PRIMARY KEY,
    NomeTraf VARCHAR(100),
    NomeArma VARCHAR(100),
    Quantidade INT,
    FOREIGN KEY (NomeTraf) REFERENCES Traficante (NomeTraf),
    FOREIGN KEY (NomeArma) REFERENCES TipoArma (NomeArma)
);

-- Tabela Fornece (relaciona Traficante, TipoArma e GrupoArmado)
DROP TABLE IF EXISTS Fornece CASCADE;

CREATE TABLE IF NOT EXISTS Fornece (
    IdFornece SERIAL PRIMARY KEY,
    CodigoG INT,
    NomeArma VARCHAR(100),
    NomeTraf VARCHAR(100),
    NumArmas INT,
    FOREIGN KEY (CodigoG) REFERENCES GrupoArmado (CodigoG),
    FOREIGN KEY (NomeArma) REFERENCES TipoArma (NomeArma),
    FOREIGN KEY (NomeTraf) REFERENCES Traficante (NomeTraf)
);

-- =========== CRIANDO FUNÇÕES & TRIGGERS ===========

-- Optei por construir uma função para garantir que todo conflito pertença a exatamente um subtipo (item 2a).
CREATE OR REPLACE FUNCTION check_total_exclusiva()
RETURNS TRIGGER AS $$
DECLARE
    count_tipos INT := 0;
BEGIN
    SELECT COUNT(*) INTO count_tipos FROM (
        SELECT CodConflito FROM Territorial WHERE CodConflito = NEW.CodConflito
        UNION ALL
        SELECT CodConflito FROM Religioso WHERE CodConflito = NEW.CodConflito
        UNION ALL
        SELECT CodConflito FROM Economico WHERE CodConflito = NEW.CodConflito
        UNION ALL
        SELECT CodConflito FROM Racial WHERE CodConflito = NEW.CodConflito
    ) AS union_all;

    IF count_tipos != 1 THEN
        RAISE EXCEPTION 'Conflito % deve pertencer a exatamente um subtipo', NEW.CodConflito;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Criação da trigger
CREATE TRIGGER trg_total_exclusiva
AFTER INSERT OR UPDATE ON Conflito
FOR EACH ROW EXECUTE FUNCTION check_total_exclusiva();

-- Optei por construir uma função para checar se uma determinada divisão possui menos de 3 chefes.
CREATE OR REPLACE FUNCTION checar_qtd_chefes_divisao(id_divisao INT)
RETURNS BOOLEAN AS $$
    DECLARE
        contagem_atual INTEGER;
    BEGIN
        select count(*)
        into contagem_atual
        from chefemilitar as c
        where c.nrodivisao = id_divisao;
        IF (contagem_atual > 3) THEN
            RAISE EXCEPTION 'Uma divisão deve possuir no máximo 3 chefes militares! Operação abortada.';
        END IF;
        return TRUE;
    END;
$$ LANGUAGE plpgsql;

-- Optei por construir uma função para checar se, após fazer as devidas inserções, os conflitos não podem ter menos de dois grupos envolvidos
CREATE OR REPLACE FUNCTION checar_qtd_grupos_conflito()
RETURNS TRIGGER AS $$
    DECLARE
        v_contagem INTEGER;
        v_codconflito_antigo INTEGER;
        v_codconflito_novo INTEGER;
    BEGIN
        IF (TG_OP = 'DELETE') THEN
            v_codconflito_antigo := OLD.codconflito;
        ELSIF (TG_OP = 'UPDATE') THEN
            v_codconflito_antigo := OLD.codconflito;
            v_codconflito_novo := NEW.codconflito;
        ELSIF (TG_OP = 'INSERT') THEN
            v_codconflito_novo := NEW.codconflito;
        END IF;
        IF v_codconflito_antigo IS NOT NULL THEN
            IF v_codconflito_antigo <> v_codconflito_novo OR v_codconflito_novo IS NULL THEN
                select count(*)
                into v_contagem
                from entpart as e
                where e.codconflito = v_codconflito_antigo;
                IF v_contagem < 2 THEN
                    RAISE EXCEPTION 'Um conflito deve envolver no mínimo 2 grupos participando! Operação abortada.';
                END IF;
            END IF;
        END IF;
        IF v_codconflito_novo IS NOT NULL THEN
            select count(*)
            into v_contagem
            from entpart as e
            where e.codconflito = v_codconflito_novo;
            IF v_contagem < 2 THEN
                RAISE EXCEPTION 'Um conflito deve envolver no mínimo 2 grupos participando! Operação abortada.';
            END IF;
        END IF;
        RETURN coalesce(NEW, OLD);
    END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_checar_minimo_grupos ON EntPart;

CREATE CONSTRAINT TRIGGER trigger_checar_minimo_grupos
AFTER INSERT OR UPDATE OR DELETE ON EntPart
DEFERRABLE INITIALLY DEFERRED
FOR EACH ROW
EXECUTE FUNCTION checar_qtd_grupos_conflito();

-- Optei por construir uma função que sincronize as baixas de um conflito com base nas baixas das divisões
CREATE OR REPLACE FUNCTION sincronizar_baixas_conflito()
RETURNS TRIGGER AS $$
DECLARE
    diferenca_baixas INT;
BEGIN
    IF (TG_OP = 'INSERT') THEN
        UPDATE conflito
        SET NumMortos = COALESCE(NumMortos, 0) + NEW.NumBaixasD
        WHERE CodConflito IN (
            SELECT CodConflito FROM EntPart WHERE CodigoG = NEW.CodigoG AND DSGrupo IS NULL
        );
        RETURN NEW;
    ELSIF (TG_OP = 'DELETE') THEN
        UPDATE conflito
        SET NumMortos = COALESCE(NumMortos, 0) - OLD.NumBaixasD
        WHERE CodConflito IN (
            SELECT CodConflito FROM EntPart WHERE CodigoG = OLD.CodigoG
        );
        RETURN OLD;
    ELSIF (TG_OP = 'UPDATE') THEN
        IF NEW.NumBaixasD <> OLD.NumBaixasD THEN
            diferenca_baixas := NEW.NumBaixasD - OLD.NumBaixasD;
            UPDATE conflito
            SET NumMortos = COALESCE(NumMortos, 0) + diferenca_baixas
            WHERE CodConflito IN (
                SELECT CodConflito FROM EntPart WHERE CodigoG = NEW.CodigoG AND DSGrupo IS NULL
            );
        END IF;
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_sincronizar_mortos ON Divisao;

CREATE TRIGGER trigger_sincronizar_mortos
AFTER INSERT OR UPDATE OR DELETE ON Divisao
FOR EACH ROW
EXECUTE FUNCTION sincronizar_baixas_conflito();

-- Optei por criar uma função que garante que o número da divisão num determinado grupo armado seja sequencial
CREATE OR REPLACE FUNCTION definir_nrodivisao_sequencial()
RETURNS TRIGGER AS $$
BEGIN
    select coalesce(MAX(NroDivisao), 0) + 1
    into NEW.nrodivisao
    from divisao as d
    where d.codigog = NEW.codigog;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_definir_nrodivisao ON Divisao;

CREATE TRIGGER trigger_definir_nrodivisao
BEFORE INSERT ON Divisao
FOR EACH ROW
EXECUTE FUNCTION definir_nrodivisao_sequencial();

ALTER TABLE ChefeMilitar ADD CONSTRAINT limite_chefes_por_divisao CHECK(checar_qtd_chefes_divisao(nrodivisao));

-- =========== POPULANDO AS TABELAS ===========
-- Inserindo Grupos Armados
INSERT INTO
    GrupoArmado (NomeGrupo)
VALUES
    ('Exército de Libertação Nacional'),
    ('Forças Armadas Revolucionárias'),
    ('Guarda Republicana'),
    ('Milícia do Povo'),
    ('Aliança Rebelde'),
    ('Império Galáctico'),
    ('Legião da Sombra'),
    ('Coalizão do Norte');

INSERT INTO
    LiderPolitico (NomeL, CodigoG, Apoios)
VALUES
    (
        'General Aladeen',
        3,
        'Apoio de nações vizinhas e conglomerados de petróleo.'
    ),
    (
        'Comandante Cobra',
        2,
        'Financiado por corporações internacionais de armas.'
    ),
    (
        'Presidente Snow',
        1,
        'Apoiado pela elite rica e pelo aparato estatal.'
    ),
    (
        'Líder Koba',
        4,
        'Suporte de facções separatistas e contrabandistas.'
    ),
    (
        'Mon Mothma',
        5,
        'Apoiada por senadores dissidentes e sistemas estelares oprimidos.'
    ),
    (
        'Imperador Palpatine',
        6,
        'Controle total do Senado Galáctico e da frota imperial.'
    ),
    (
        'Lorde das Sombras',
        7,
        'Poder derivado de fontes arcanas e cultos secretos.'
    ),
    (
        'Rei do Norte',
        8,
        'Lealdade dos clãs das montanhas e cidades-estado do norte.'
    );

-- Inserindo Divisões dos Grupos Armados
INSERT INTO
    Divisao (
        CodigoG,
        NumBaixasD,
        Barcos,
        Tanques,
        Avioes,
        Homens
    )
VALUES
    (1, 120, 10, 50, 20, 5000), -- Exército de Libertação Nacional
    (1, 250, 5, 80, 15, 7000), -- Exército de Libertação Nacional
    (2, 500, 0, 120, 30, 10000), -- Forças Armadas Revolucionárias
    (3, 80, 30, 150, 50, 12000), -- Guarda Republicana
    (4, 300, 2, 40, 5, 4500), -- Milícia do Povo
    (5, 350, 15, 30, 150, 8000), -- Aliança Rebelde
    (6, 1500, 500, 2000, 1000, 50000), -- Império Galáctico
    (6, 1200, 400, 1500, 800, 45000), -- Império Galáctico
    (7, 400, 5, 100, 10, 6000), -- Legião da Sombra
    (8, 200, 20, 150, 5, 9000);

-- Coalizão do Norte
-- Inserindo Chefes Militares
INSERT INTO
    ChefeMilitar (Faixa, NroDivisao, CodigoG, NomeL)
VALUES
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
INSERT INTO
    Conflito (Nome, NumFeridos, NumMortos, TipoConf)
VALUES
    ('Guerra do Deserto', 5000, 2000, 'Economico'),
    (
        'Insurreição da Primavera',
        12000,
        4500,
        'Territorial'
    ),
    ('Cruzada Santa do Norte', 8000, 3200, 'Religioso'),
    ('Guerra de Segregação', 20000, 9000, 'Racial'),
    ('Batalha pela Água', 3000, 1000, 'Economico'),
    (
        'Guerra Civil Galáctica',
        1500000,
        700000,
        'Territorial'
    ),
    ('A Longa Noite', 50000, 25000, 'Racial'),
    (
        'Guerra das Especiarias',
        25000,
        8000,
        'Economico'
    );

-- Detalhando tipos de conflitos
INSERT INTO
    Economico (CodConflito, MatPrima)
VALUES
    (1, 'Petróleo'),
    (5, 'Água Potável'),
    (8, 'Especiaria Melange');

INSERT INTO
    Territorial (CodConflito, Regiao)
VALUES
    (2, 'Província do Norte'),
    (6, 'Borda Exterior da Galáxia');

INSERT INTO
    Religioso (CodConflito, Religiao)
VALUES
    (3, 'Fé do Solstício');

INSERT INTO
    Racial (CodConflito, Etnia)
VALUES
    (4, 'Povo do Vale'),
    (7, 'Caminhantes Brancos');

-- Inserindo países nos conflitos
INSERT INTO
    ConflitoPais (CodConflito, Pais)
VALUES
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
BEGIN;
INSERT INTO
    EntPart (CodigoG, CodConflito, DEGrupo, DSGrupo)
VALUES
    (1, 2, '2023-01-15', NULL),
    (2, 2, '2023-01-20', NULL),
    -- (3, 1, '2022-05-10', '2024-08-20'),
    -- (4, 4, '2021-11-01', NULL),
    -- (3, 3, '2023-03-12', NULL),
    (5, 6, '2005-05-19', '2010-10-20'),
    (6, 6, '2005-05-19', '2010-10-20'),
    (7, 7, '2018-01-01', NULL),
    (8, 7, '2018-01-01', NULL);
    -- (1, 8, '2024-01-01', NULL);
COMMIT;

-- Inserindo Organizações Mediadoras
INSERT INTO
    OrganizacaoM (NomeOrg, Tipo, OrgLider)
VALUES
    (
        'Cruz Vermelha Internacional',
        'não governamental',
        NULL
    ),
    ('Nações Unidas', 'internacional', NULL),
    (
        'Médicos Sem Fronteiras',
        'não governamental',
        NULL
    ),
    ('Ordem Jedi', 'não governamental', NULL),
    ('Guilda Espacial', 'governamental', NULL);

-- Inserindo Mediação das Organizações nos Conflitos
INSERT INTO
    EntradMed (
        CodigoOrg,
        CodConflito,
        DEMedia,
        DSMedia,
        NumPessoas,
        TipoAjuda
    )
VALUES
    (1, 2, '2023-02-01', NULL, 50, 'médica'),
    (2, 2, '2023-03-10', NULL, 25, 'diplomática'),
    (3, 4, '2022-01-15', NULL, 80, 'médica'),
    (
        2,
        1,
        '2022-06-01',
        '2024-07-30',
        40,
        'presencial'
    ),
    (
        4,
        6,
        '2006-01-01',
        '2006-05-01',
        5,
        'diplomática'
    ),
    (5, 8, '2024-02-10', NULL, 150, 'presencial'),
    (1, 7, '2018-06-20', NULL, 30, 'médica');

-- Inserindo Diálogos
INSERT INTO
    Dialoga (NomeL, CodigoOrg)
VALUES
    ('Presidente Snow', 2),
    ('General Aladeen', 1),
    ('Líder Koba', 3),
    ('Mon Mothma', 4),
    ('Imperador Palpatine', 5),
    ('Rei do Norte', 1);

-- Inserindo Traficantes
INSERT INTO
    Traficante (NomeTraf)
VALUES
    ('Viktor Bout'),
    ('Adnan Khashoggi'),
    ('Lord of War'),
    ('Hondo Ohnaka'),
    ('A Baronesa');

-- Inserindo Tipos de Armas
INSERT INTO
    TipoArma (NomeArma, Indicador)
VALUES
    ('Barret M82', 9),
    ('M200 Intervention', 10),
    ('AK-47', 7),
    ('RPG-7', 8),
    ('Rifle Blaster E-11', 6),
    ('Sabre de Luz', 10),
    ('Canhão de Íons', 8);

-- Inserindo o que cada traficante pode fornecer
INSERT INTO
    PodeFornecer (NomeTraf, NomeArma, Quantidade)
VALUES
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
INSERT INTO
    Fornece (CodigoG, NomeArma, NomeTraf, NumArmas)
VALUES
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
