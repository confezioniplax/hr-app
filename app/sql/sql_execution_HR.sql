-- ==========================================================
-- DATABASE: PLAX
-- VERSIONE: 1.3 (Ottobre 2025) — modulo su DEPARTMENTS
-- ==========================================================

DROP DATABASE IF EXISTS plax;
CREATE DATABASE plax CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE plax;

-- ==========================================================
-- 1) ANAGRAFICHE DI BASE
-- ==========================================================

CREATE TABLE departments (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  name VARCHAR(100) NOT NULL,
  module_code VARCHAR(40) NULL COMMENT 'Es. "Mod. 021 S/T/A" — codice modulo del reparto',
  active TINYINT(1) NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);


CREATE TABLE operators (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  first_name VARCHAR(60) NOT NULL,
  last_name  VARCHAR(60) NOT NULL,
  email VARCHAR(150) NULL UNIQUE,
  user_password VARCHAR(255) NULL,
  role VARCHAR(20) NULL DEFAULT 'HR',
  badge_code VARCHAR(40) NULL,
  phone VARCHAR(40) NULL,
  fiscal_code VARCHAR(32) NULL,                -- CF; metti UNIQUE se vuoi vincolo forte
  birth_place VARCHAR(120) NULL,
  birth_date DATE NULL,
  address VARCHAR(255) NULL,
  active TINYINT(1) NOT NULL DEFAULT 1,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
  KEY idx_operators_name (last_name, first_name),
  KEY idx_operators_cf (fiscal_code)
);



CREATE TABLE operator_departments (
  operator_id   BIGINT NOT NULL,
  department_id BIGINT NOT NULL,
  PRIMARY KEY (operator_id, department_id),
  CONSTRAINT fk_opdept_op  FOREIGN KEY (operator_id)   REFERENCES operators(id)   ON DELETE CASCADE,
  CONSTRAINT fk_opdept_dep FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE
);

CREATE INDEX idx_opdept_dept ON operator_departments (department_id);

-- ==========================================================
-- 7) CERTIFICAZIONI / BREVETTI OPERATORI
-- ==========================================================

CREATE TABLE operator_cert_types (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  code VARCHAR(40) NOT NULL UNIQUE,             -- es: ANTINCENDIO, PRIMO_SOCCORSO, CARRELLI_ELEV, DIISOCIANATI, RLS, RSPP
  description VARCHAR(120) NULL,
  requires_expiry TINYINT(1) NOT NULL DEFAULT 1
);

CREATE TABLE operator_certifications (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  operator_id BIGINT NOT NULL,
  cert_type_id BIGINT NOT NULL,
  status ENUM('OK','MANCA','ND') NOT NULL DEFAULT 'OK',
  issue_date DATE NULL,
  expiry_date DATE NULL,
  notes VARCHAR(255) NULL,
  created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_op_cert (operator_id, cert_type_id),
  CONSTRAINT fk_opcert_op   FOREIGN KEY (operator_id) REFERENCES operators(id) ON DELETE CASCADE,
  CONSTRAINT fk_opcert_type FOREIGN KEY (cert_type_id) REFERENCES operator_cert_types(id) ON DELETE CASCADE
);


/* ===========================
   POPOLAMENTO BASE (PLAX v1.3)
   =========================== */

-- 1) REPARTI (con modulo dove previsto per le schede)
INSERT INTO departments (id, name, module_code) VALUES
(1, 'STAMPA',        'Mod. 021 S'),
(2, 'TAGLIO',        'Mod. 021 T'),
(3, 'ACCOPPIAMENTO', 'Mod. 021 A'),
(4, 'SALDATURA',      NULL),
(5, 'MAGAZZINO',      NULL),
(6, 'UFFICIO',        NULL),
(7, 'CEO',            NULL),
(8, 'MANAGEMENT',     NULL);

-- 2) TIPI MACCHINA

-- 5) OPERATORI (35)  — anagrafica in tabella operators
INSERT INTO operators
(id, first_name, last_name, phone, fiscal_code, birth_place, birth_date, address, role, active)
VALUES
(1,  'ARTUR',      'ASEVSCHI',           '3210413912','SVSRTR90R07Z140N','Moldavia',           '1990-10-07','Galleria P.Venturi 4 - Savignano sul Rubicone - FC','HR',1),
(2,  'ALBANO',     'BALSOMINI',          '3210413912','BLSLBN68C03L500D','Urbino - PU',        '1968-03-03','Via S. Giovanni 19 - Misano Adriatica - RN','HR',1),
(3,  'GIANFRANCESCO','BARONCINI',        '3210413912','BRNGFR79T31F137L','Novafeltria - RN',   '1979-12-31','Via D. Raggi 42 - Savignano sul Rubicone - FC','HR',1),
(4,  'MIKALAI',    'BENZI',              '3210413912','BNZMKL85T29Z139P','Bielorussia',        '1985-12-29','Via Irisi Versari 80 - Cesena - FC','HR',1),
(5,  'LUCA',       'BORGHETTI',          '3210413912','BRGLCU74D01C573V','Cesena - FC',        '1974-04-01','Via Ravennate 4442 - Cesena - FC','HR',1),
(6,  'GABRIEL',    'BUFNILA',            '3210413912','BFNMSG91E18Z129Y','Romania',            '1991-05-18','Via Torriana 35 - Cesena - FC','HR',1),
(7,  'ELIA',       'BUZZONE',            '3210413912','BZZLEI97P15C573U','Cesena - FC',        '1997-09-15','Via Erzegovina 22 - S. Mauro Pascoli - FC','HR',1),
(8,  'IVANO',      'CAPUTI',             '3210413912','CPTVNI84D18H703I','Salerno - CE',       '1984-04-18','Via Ronta 2 - Gatteo - FC','HR',1),
(9,  'MIRCO',      'CELLI',              '3210413912','CLLMRC71C18H274J','Riccione - RN',      '1971-03-18','Viale Riva del Garda 13 - Riccione - RN','HR',1),
(10, 'FRANCESCO',  'CHIARABINI',         '3210413912','CHRFNC77C12I472H','Savignano S/R - FC', NULL,'Via S. Vito 99 - Savignano sul Rubicone - FC','HR',1),
(11, 'STEFANO',    'COCCIA',             '3210413912','CCCSFN92A13D643N','Foggia - FG',        '1992-01-13','Via Don L. Praconi 58 - Gambettola - FC','HR',1),
(12, 'LORENZO',    'COLONNA',            '3210413912','CLNLNZ04P02H926U','S. Giovanni Rotondo - FG','2004-09-02','Via Ferrari n.2 - Savignano sul Rubicone - FC','HR',1),
(13, 'EMANUELE',   'D\'ANGELI',          '3210413912','DNGMNL84A18H834E','S. Felice a Cancello - CE','1984-01-18','Via dello sport 9 - Gambettola - FC','HR',1),
(14, 'MATTIA',     'DEL VECCHIO',        '3210413912','DLVMTT05R31H294Q','Rimini - RN',        '2005-10-31','Via P. Zangheri 61 - Savignano sul Rubicone - FC','HR',1),
(15, 'GIORGIA',    'DELORENZI',          '3210413912','DLRGRG98D63C573U','Cesena - FC',        '1998-04-23','Via Abbondanza 2 - Gatteo - FC','HR',1),
(16, 'PAPA GORA',  'DIEYE',              '3210413912','DYIPGR77E17Z343J','Senegal',            '1977-05-17','Via Roma 17 - San Mauro Pascoli - FC','HR',1),
(17, 'IVAN GEORGIEV','DOBREV',           '3210413912','DBRVGR88L147Z104W','Bulgaria',          '1988-07-17','Via Violetti 879 - Cesena - FC','HR',1),
(18, 'FLAVIO',     'FORNASARI',          '3210413912','FRNFLV68S18D705M','Forlimpopoli - FC', '1968-11-18','Via Mazzolini 43 - Forlimpopoli - FC','HR',1),
(19, 'MIRCO',      'FRANI',              '3210413912','FRNMRC74C03C573E','Cesena - FC',        '1974-03-03','Via A. Moroni 49 - Savignano sul Rubicone - FC','HR',1),
(20, 'OMAR',       'GALASSI',            '3210413912','GLSMRO76B12C573A','Cesena - FC',        '1976-02-12','Via N. Sauro 37/A - Gambettola - FC','HR',1),
(21, 'ALEX',       'GARAVELLI',          '3210413912','GRVLXA01P20C573L','Cesena - FC',        '2001-09-20','Via Guerrini 5 - Savignano sul Rubicone - FC','HR',1),
(22, 'MARCO',      'GOZI',               '3210413912','GZOMRC67L13H294H','Rimini - RN',        '1967-07-13','Via C. Menotti 31/a - Santarcangelo - RN','HR',1),
(23, 'ADELINA',    'KANINA',             '3210413912','KNNDLN77E59Z100K','Albania',            '1977-05-19','Via S. Pellico 58 - Savignano sul Rubicone - FC','HR',1),
(24, 'MARCO',      'LEONELLI',           '3210413912','LNLMRC69D26D704Q','Forlì - FC',         '1967-04-26','Via Nansen 27 - Lido di Classe - RA','HR',1),
(25, 'MASSIMO',    'LEONELLI',           '3210413912','LNLMSM63S10D704O','Forlì - FC',         '1963-11-10','Via Bellini 15 - Savignano sul Rubicone - FC','HR',1),
(26, 'NICOLA',     'LUPINACCI',          '3210413912','LPNNCL85B08D086I','Cosenza - CS',       '1985-02-08','Via Dogana 1630 - Verucchio - RN','HR',1),
(27, 'ANTONIO',    'MAESTRELLI',         '3210413912','MSTNTN64M28F704X','Monza',             '1964-08-28','Via Marconi 18 - Savignano sul Rubicone - FC','HR',1),
(28, 'DONATO',     'MORRICA',            '3210413912','MRRDNT78B06I158B','San Severo - FG',   '1978-02-06','Via dei girasoli 3 - Gatteo - FC','HR',1),
(29, 'GABRIELE',   'NERI',               '3210413912','NREGRL75R11D704B','Forlì - FC',         '1975-10-11','Via A. Venturini 61 - Forlì - FC','HR',1),
(30, 'PATRIZIA',   'PELLEGRINI',         '3210413912','PLLPRZ66H66C573Y','Cesena - FC',        '1966-06-26','Via G. Galilei 18 - Savignano sul Rubicone - FC','HR',1),
(31, 'GIACOMO',    'PROTA',              '3210413912','PRTGCM64M11D704U','Forlì - FC',         '1964-08-11','Via del Partigiano 44 - Meldola - FC','HR',1),
(32, 'ILARIA',     'RANDELLI',           '3210413912','RNDLRI89T60G791G','Reggio Calabria',    '1989-12-20','Via della Repubblica 25E - Savignano sul Rubicone - FC','HR',1),
(33, 'CLAUDIO',    'TORDI',              '3210413912','TRDCLD76S02H294N','Rimini - RN',        '1976-11-02','Via Montalaccio n.1 - Rimini - RN','HR',1),
(34, 'LORIS',      'VENTURI',            '3210413912','VNTLRS87P17C573U','Cesena - FC',        '1987-09-17','Via de. Raggi 14 - Longiano - FC','HR',1),
(35, 'MIRCO',      'VENTURINI',          '3210413912','VNTMRC97E12C573B','Cesena - FC',        '1997-05-12','Via Galeazza 108 - Cesena - FC','HR',1),
-- aggiunto perché citato nell’assegnazione reparti
(36, 'RICCARDO',   'LEONELLI',           NULL,       NULL,               NULL,                 NULL,        NULL,'HR',1);

-- 6) OPERATORI ↔ REPARTI (assegnazioni)
-- Nota: per le schede lavoro userai STAMPA/TAGLIO/ACCOPPIAMENTO; gli altri reparti servono per filtri/HR.
INSERT INTO operator_departments (operator_id, department_id) VALUES
-- Artur: tutto (reparti produttivi)
(1,1),(1,2),(1,3),

-- Balsomini: saldatura
(2,4),

-- Baroncini: taglio
(3,2),

-- Benzi: stampa
(4,1),

-- Borghetti: magazzino
(5,5),

-- Bufnila: stampa
(6,1),

-- Buzzone: taglio + accoppiamento
(7,2),(7,3),

-- Caputi: stampa
(8,1),

-- Celli: accoppiamento
(9,3),

-- Chiarabini: magazzino
(10,5),

-- Coccia: stampa
(11,1),

-- Colonna: stampa
(12,1),

-- D'Angeli: stampa
(13,1),

-- Del Vecchio: stampa
(14,1),

-- Delorenzi Giorgia: ufficio
(15,6),

-- Dieye Papa Gora: stampa
(16,1),

-- Dobrev Ivan: accoppiamento
(17,3),

-- Frani: taglio
(19,2),

-- Galassi Omar: ufficio
(20,6),

-- Garavelli Alex: stampa
(21,1),

-- Gozi Marco: taglio
(22,2),

-- Kanina Adelina: saldatura
(23,4),

-- Leonelli Marco: CEO
(24,7),

-- Leonelli Massimo: CEO
(25,7),

-- Lupinacci Nicola: taglio
(26,2),

-- Randelli Ilaria: ufficio
(32,6),

-- Riccardo Leonelli: management
(36,8),

-- Maestrelli Antonio: stampa
(27,1),

-- Morrica Donato: magazzino
(28,5),

-- Pellegrini Patrizia: ufficio
(30,6),

-- Prota Giacomo: taglio
(31,2),

-- Tordi Claudio: stampa
(33,1),

-- Venturi Loris: stampa
(34,1),

-- Venturini Mirco: accoppiamento
(35,3);


UPDATE operators
SET
  email = 'riccardo@plaxpackaging.it',
  user_password = '$2b$12$uRT7LwdlAayVqGqwLUbnNOqQVcchrQNed7bsxGBup4WuwjlypVOM2',
  role = 'HR',
  active = 1
WHERE
  last_name = 'Leonelli'
  AND first_name = 'Riccardo';


USE plax;

-- hire_date
SET @sql := (
  SELECT IF(
    EXISTS(SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
           WHERE TABLE_SCHEMA = DATABASE()
             AND TABLE_NAME = 'operators'
             AND COLUMN_NAME = 'hire_date'),
    'SELECT 1',  -- già esiste: no-op
    'ALTER TABLE operators ADD COLUMN hire_date DATE NULL AFTER birth_date'
  )
);
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- contract_type
SET @sql := (
  SELECT IF(
    EXISTS(SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
           WHERE TABLE_SCHEMA = DATABASE()
             AND TABLE_NAME = 'operators'
             AND COLUMN_NAME = 'contract_type'),
    'SELECT 1',
    'ALTER TABLE operators ADD COLUMN contract_type VARCHAR(50) NULL AFTER hire_date'
  )
);
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- contract_expiry
SET @sql := (
  SELECT IF(
    EXISTS(SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
           WHERE TABLE_SCHEMA = DATABASE()
             AND TABLE_NAME = 'operators'
             AND COLUMN_NAME = 'contract_expiry'),
    'SELECT 1',
    'ALTER TABLE operators ADD COLUMN contract_expiry DATE NULL AFTER contract_type'
  )
);
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- level (quotato con backtick)
SET @sql := (
  SELECT IF(
    EXISTS(SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
           WHERE TABLE_SCHEMA = DATABASE()
             AND TABLE_NAME = 'operators'
             AND COLUMN_NAME = 'level'),
    'SELECT 1',
    'ALTER TABLE operators ADD COLUMN `level` VARCHAR(20) NULL AFTER contract_expiry'
  )
);
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- ral
SET @sql := (
  SELECT IF(
    EXISTS(SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
           WHERE TABLE_SCHEMA = DATABASE()
             AND TABLE_NAME = 'operators'
             AND COLUMN_NAME = 'ral'),
    'SELECT 1',
    'ALTER TABLE operators ADD COLUMN ral DECIMAL(12,2) NULL AFTER `level`'
  )
);
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;


-- citizenship
SET @sql := (
  SELECT IF(
    EXISTS(SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
           WHERE TABLE_SCHEMA = DATABASE()
             AND TABLE_NAME = 'operators'
             AND COLUMN_NAME = 'citizenship'),
    'SELECT 1',
    'ALTER TABLE operators ADD COLUMN citizenship VARCHAR(80) NULL AFTER birth_date'
  )
);
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- education_level
SET @sql := (
  SELECT IF(
    EXISTS(SELECT 1 FROM INFORMATION_SCHEMA.COLUMNS
           WHERE TABLE_SCHEMA = DATABASE()
             AND TABLE_NAME = 'operators'
             AND COLUMN_NAME = 'education_level'),
    'SELECT 1',
    'ALTER TABLE operators ADD COLUMN education_level VARCHAR(60) NULL COMMENT ''Es: Nessuno, Licenza media, Diploma, Laurea triennale, Laurea magistrale, Master, Dottorato, Altro'' AFTER citizenship'
  )
);
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- indici per filtri veloci (se non già presenti)
SET @sql := (
  SELECT IF(
    EXISTS(SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS
           WHERE TABLE_SCHEMA = DATABASE()
             AND TABLE_NAME = 'operators'
             AND INDEX_NAME = 'idx_operators_citizenship'),
    'SELECT 1',
    'ALTER TABLE operators ADD INDEX idx_operators_citizenship (citizenship)'
  )
);
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

SET @sql := (
  SELECT IF(
    EXISTS(SELECT 1 FROM INFORMATION_SCHEMA.STATISTICS
           WHERE TABLE_SCHEMA = DATABASE()
             AND TABLE_NAME = 'operators'
             AND INDEX_NAME = 'idx_operators_education'),
    'SELECT 1',
    'ALTER TABLE operators ADD INDEX idx_operators_education (education_level)'
  )
);
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;



/* ============================
   CERTIFICAZIONII POPOLAMENTO 
   ============================ */
/* ============================
   TIPI certificazione
   ============================ */
INSERT INTO operator_cert_types (code, description, requires_expiry)
VALUES
  ('SICUREZZA_GEN',  'Formazione Sicurezza Generale',                 0),
  ('SICUREZZA_SPEC', 'Formazione Sicurezza Specifica',                1),
  ('ESERC_EMERG_CIV_29', 'Esercitazioni Emergenza (CIV.29)',          0)
ON DUPLICATE KEY UPDATE
  description = VALUES(description),
  requires_expiry = VALUES(requires_expiry);

/* IDs dei tipi */
SET @ct_gen   := (SELECT id FROM operator_cert_types WHERE code='SICUREZZA_GEN');
SET @ct_spec  := (SELECT id FROM operator_cert_types WHERE code='SICUREZZA_SPEC');
SET @ct_emerg := (SELECT id FROM operator_cert_types WHERE code='ESERC_EMERG_CIV_29');

/* ============================
   SICUREZZA GENERALE (issue_date)
   ============================ */
INSERT INTO operator_certifications (operator_id, cert_type_id, status, issue_date, expiry_date, notes)
VALUES
  (1, @ct_gen,  'OK', '2018-10-11', NULL, NULL),
  (2, @ct_gen,  'OK', '2019-06-01', NULL, NULL),
  (3, @ct_gen,  'OK', '2019-06-01', NULL, NULL),
  (4, @ct_gen,  'OK', '2027-10-29', NULL, NULL),
  (5, @ct_gen,  'OK', '2024-05-31', NULL, NULL),
  (6, @ct_gen,  'OK', '2019-06-08', NULL, NULL),
  -- (7) MANCA → nessuna insert
  (8, @ct_gen,  'OK', '2019-11-25', NULL, NULL),
  (9, @ct_gen,  'OK', '2021-09-30', NULL, NULL),
  (10, @ct_gen, 'OK', '2019-05-31', NULL, NULL),
  (11, @ct_gen, 'OK', '2027-10-29', NULL, NULL),
  -- (12) MANCA
  (13, @ct_gen, 'OK', '2024-09-23', NULL, NULL),
  -- (14) MANCA
  (15, @ct_gen, 'OK', '2028-07-04', NULL, NULL),
  (16, @ct_gen, 'OK', '2017-07-27', NULL, NULL),
  (17, @ct_gen, 'OK', '2019-05-31', NULL, NULL),
  (18, @ct_gen, 'OK', '2021-09-29', NULL, NULL),
  (19, @ct_gen, 'OK', '2019-06-08', NULL, NULL),
  (20, @ct_gen, 'OK', '2021-09-29', NULL, NULL),
  -- (21) MANCA
  (22, @ct_gen, 'OK', '2027-11-05', NULL, NULL),
  (23, @ct_gen, 'OK', '2024-05-31', NULL, NULL),
  (24, @ct_gen, 'OK', '2019-06-08', NULL, NULL),
  -- (25) vuoto → trattiamo come MANCA → nessuna insert
  (26, @ct_gen, 'OK', '2019-05-31', NULL, NULL),
  -- (27) MANCA
  -- (28) MANCA
  (29, @ct_gen, 'OK', '2022-11-05', NULL, NULL),
  (30, @ct_gen, 'OK', '2024-05-31', NULL, NULL),
  (31, @ct_gen, 'OK', '2019-06-08', NULL, NULL),
  -- (32) foglio riporta “SPEC”/MANCA → per prudenza non inseriamo GEN
  (33, @ct_gen, 'OK', '2023-11-23', NULL, NULL),
  (34, @ct_gen, 'OK', '2019-05-31', NULL, NULL)
  -- (35) riportato come SPEC/MANCA → niente GEN
ON DUPLICATE KEY UPDATE
  status      = VALUES(status),
  issue_date  = VALUES(issue_date),
  expiry_date = VALUES(expiry_date),
  notes       = VALUES(notes);

/* ============================
   SICUREZZA SPECIFICA (expiry_date)
   ============================ */
INSERT INTO operator_certifications (operator_id, cert_type_id, status, issue_date, expiry_date, notes)
VALUES
  (1,  @ct_spec, 'OK', NULL, '2023-10-11', NULL),
  (2,  @ct_spec, 'OK', NULL, '2029-11-16', NULL),
  (3,  @ct_spec, 'OK', NULL, '2029-11-16', NULL),
  (4,  @ct_spec, 'OK', NULL, '2027-10-29', NULL),
  (5,  @ct_spec, 'OK', NULL, '2029-11-16', NULL),
  (6,  @ct_spec, 'OK', NULL, '2029-11-16', NULL),
  -- (7) MANCA
  (8,  @ct_spec, 'OK', NULL, '2024-11-25', NULL),
  (9,  @ct_spec, 'OK', NULL, '2029-11-16', NULL),
  (10, @ct_spec, 'OK', NULL, '2029-11-23', NULL),
  (11, @ct_spec, 'OK', NULL, '2027-10-29', NULL),
  -- (12) MANCA
  (13, @ct_spec, 'OK', NULL, '2027-07-06', NULL),
  -- (14) MANCA
  (15, @ct_spec, 'OK', NULL, '2027-11-05', NULL),
  (16, @ct_spec, 'OK', NULL, '2029-11-30', NULL),
  (17, @ct_spec, 'OK', NULL, '2029-11-23', NULL),
  (18, @ct_spec, 'OK', NULL, '2029-11-16', NULL),
  (19, @ct_spec, 'OK', NULL, '2029-11-23', NULL),
  (20, @ct_spec, 'OK', NULL, '2026-09-30', NULL),
  (21, @ct_spec, 'OK', NULL, '2029-11-30', NULL),
  (22, @ct_spec, 'OK', NULL, '2027-10-29', NULL),
  (23, @ct_spec, 'OK', NULL, '2029-11-30', NULL),
  (24, @ct_spec, 'OK', NULL, '2024-06-08', NULL),
  -- (25) vuoto → nessuna insert
  (26, @ct_spec, 'OK', NULL, '2029-11-23', NULL),
  -- (27) MANCA
  (28, @ct_spec, 'OK', NULL, '2029-02-26', NULL),
  (29, @ct_spec, 'OK', NULL, '2027-11-05', NULL),
  (30, @ct_spec, 'OK', NULL, '2029-11-16', NULL),
  (31, @ct_spec, 'OK', NULL, '2029-11-23', NULL),
  -- (32) MANCA
  (33, @ct_spec, 'OK', NULL, '2028-11-23', NULL),
  (34, @ct_spec, 'OK', NULL, '2029-11-23', NULL)
  -- (35) MANCA
ON DUPLICATE KEY UPDATE
  status      = VALUES(status),
  issue_date  = VALUES(issue_date),
  expiry_date = VALUES(expiry_date),
  notes       = VALUES(notes);

/* ============================
   ESERC. EMERG. CIV.29 (senza date)
   ============================ */
INSERT INTO operator_certifications (operator_id, cert_type_id, status, issue_date, expiry_date, notes)
VALUES
  (3,  @ct_emerg, 'OK', NULL, NULL, NULL),
  (5,  @ct_emerg, 'OK', NULL, NULL, NULL),
  (6,  @ct_emerg, 'OK', NULL, NULL, NULL),
  (9,  @ct_emerg, 'OK', NULL, NULL, NULL),
  (10, @ct_emerg, 'OK', NULL, NULL, NULL),
  (16, @ct_emerg, 'OK', NULL, NULL, NULL),
  (17, @ct_emerg, 'OK', NULL, NULL, NULL),
  (20, @ct_emerg, 'OK', NULL, NULL, NULL),
  (24, @ct_emerg, 'OK', NULL, NULL, NULL),
  (26, @ct_emerg, 'OK', NULL, NULL, NULL),
  (30, @ct_emerg, 'OK', NULL, NULL, NULL),
  (31, @ct_emerg, 'OK', NULL, NULL, NULL),
  (33, @ct_emerg, 'OK', NULL, NULL, NULL),
  (34, @ct_emerg, 'OK', NULL, NULL, NULL)
ON DUPLICATE KEY UPDATE
  status      = VALUES(status),
  issue_date  = VALUES(issue_date),
  expiry_date = VALUES(expiry_date),
  notes       = VALUES(notes);

/* ============================================
   1) TIPI CERTIFICAZIONE (crea/aggiorna)
   ============================================ */
INSERT INTO operator_cert_types (code, description, requires_expiry) VALUES
  ('DIISOCIANATI',   'Formazione uso diisocianati',           1),
  ('ANTINCENDIO',    'Formazione antincendio',                1),
  ('PRIMO_SOCCORSO', 'Formazione primo soccorso',             1),
  ('CARRELLI_ELEV',  'Abilitazione carrelli elevatori',       1),
  ('RLS',            'Rappresentante dei Lavoratori Sicurezza', 1),
  ('RSPP',           'Responsabile del Servizio Prevenzione e Protezione', 1)
ON DUPLICATE KEY UPDATE
  description = VALUES(description),
  requires_expiry = VALUES(requires_expiry);

SET @ct_dii  := (SELECT id FROM operator_cert_types WHERE code='DIISOCIANATI');
SET @ct_anti := (SELECT id FROM operator_cert_types WHERE code='ANTINCENDIO');
SET @ct_ps   := (SELECT id FROM operator_cert_types WHERE code='PRIMO_SOCCORSO');
SET @ct_ce   := (SELECT id FROM operator_cert_types WHERE code='CARRELLI_ELEV');
SET @ct_rls  := (SELECT id FROM operator_cert_types WHERE code='RLS');
SET @ct_rspp := (SELECT id FROM operator_cert_types WHERE code='RSPP');

/* ============================================
   2) DIISOCIANATI (expiry_date)
   ============================================ */
INSERT INTO operator_certifications (operator_id, cert_type_id, status, issue_date, expiry_date, notes) VALUES
  (4,  @ct_dii, 'OK', NULL, '2029-02-08', NULL),
  (6,  @ct_dii, 'OK', NULL, '2029-02-08', NULL),
  (9,  @ct_dii, 'OK', NULL, '2029-02-08', NULL),
  (11, @ct_dii, 'OK', NULL, '2029-02-08', NULL),
  (16, @ct_dii, 'OK', NULL, '2029-02-08', NULL),
  (17, @ct_dii, 'OK', NULL, '2029-02-08', NULL),
  (21, @ct_dii, 'OK', NULL, '2029-02-08', NULL),
  (34, @ct_dii, 'OK', NULL, '2029-02-08', NULL)
ON DUPLICATE KEY UPDATE status=VALUES(status), issue_date=VALUES(issue_date), expiry_date=VALUES(expiry_date), notes=VALUES(notes);

/* ============================================
   3) ANTINCENDIO (expiry_date)
   ============================================ */
INSERT INTO operator_certifications (operator_id, cert_type_id, status, issue_date, expiry_date, notes) VALUES
  (1,  @ct_anti, 'OK', NULL, '2028-03-13', NULL),
  (2,  @ct_anti, 'OK', NULL, '2026-03-24', NULL),
  (3,  @ct_anti, 'OK', NULL, '2025-10-27', NULL),
  (5,  @ct_anti, 'OK', NULL, '2028-03-13', NULL),
  (9,  @ct_anti, 'OK', NULL, '2024-10-11', 'da verificare'),
  (15, @ct_anti, 'OK', NULL, '2028-03-13', NULL),
  (24, @ct_anti, 'OK', NULL, '2026-01-18', NULL),
  (25, @ct_anti, 'OK', NULL, '2025-10-27', NULL)
ON DUPLICATE KEY UPDATE status=VALUES(status), issue_date=VALUES(issue_date), expiry_date=VALUES(expiry_date), notes=VALUES(notes);

/* ============================================
   4) PRIMO SOCCORSO (expiry_date)
   ============================================ */
INSERT INTO operator_certifications (operator_id, cert_type_id, status, issue_date, expiry_date, notes) VALUES
  (1,  @ct_ps, 'OK', NULL, '2024-10-13', NULL),
  (2,  @ct_ps, 'OK', NULL, '2027-11-29', NULL),
  (5,  @ct_ps, 'OK', NULL, '2025-11-25', NULL),
  (9,  @ct_ps, 'OK', NULL, '2027-11-29', NULL),
  (15, @ct_ps, 'OK', NULL, '2025-11-25', NULL),
  (18, @ct_ps, 'OK', NULL, '2027-11-29', NULL),
  (24, @ct_ps, 'OK', NULL, '2029-11-29', NULL),
  (25, @ct_ps, 'OK', NULL, '2027-11-29', NULL)
ON DUPLICATE KEY UPDATE status=VALUES(status), issue_date=VALUES(issue_date), expiry_date=VALUES(expiry_date), notes=VALUES(notes);

/* ============================================
   5) CARRELLI ELEVATORI (expiry_date)
   ============================================ */
INSERT INTO operator_certifications (operator_id, cert_type_id, status, issue_date, expiry_date, notes) VALUES
  (1,  @ct_ce, 'OK', NULL, '2028-04-29', NULL),
  (2,  @ct_ce, 'OK', NULL, '2025-10-24', NULL),
  (3,  @ct_ce, 'OK', NULL, '2028-04-29', NULL),
  (4,  @ct_ce, 'OK', NULL, '2028-12-02', NULL),
  (5,  @ct_ce, 'OK', NULL, '2025-10-10', NULL),
  (6,  @ct_ce, 'OK', NULL, '2025-10-24', NULL),
  (9,  @ct_ce, 'OK', NULL, '2028-04-29', NULL),
  (10, @ct_ce, 'OK', NULL, '2028-04-29', NULL),
  (11, @ct_ce, 'OK', NULL, '2028-12-02', NULL),
  (13, @ct_ce, 'OK', NULL, '2024-11-12', NULL),
  (16, @ct_ce, 'OK', NULL, '2025-10-24', NULL),
  (17, @ct_ce, 'OK', NULL, '2025-10-24', NULL),
  (20, @ct_ce, 'OK', NULL, '2028-04-29', NULL),
  (21, @ct_ce, 'OK', NULL, '2026-01-28', NULL),
  (22, @ct_ce, 'OK', NULL, '2026-01-28', NULL),
  (25, @ct_ce, 'OK', NULL, '2028-04-29', NULL),
  (26, @ct_ce, 'OK', NULL, '2028-04-29', NULL),
  (28, @ct_ce, 'OK', NULL, '2029-07-26', NULL),
  (31, @ct_ce, 'OK', NULL, '2028-12-02', NULL),
  (33, @ct_ce, 'OK', NULL, '2028-11-24', NULL),
  (34, @ct_ce, 'OK', NULL, '2028-04-29', NULL)
ON DUPLICATE KEY UPDATE status=VALUES(status), issue_date=VALUES(issue_date), expiry_date=VALUES(expiry_date), notes=VALUES(notes);

/* ============================================
   6) RLS / RSPP (expiry_date)
   ============================================ */
INSERT INTO operator_certifications (operator_id, cert_type_id, status, issue_date, expiry_date, notes) VALUES
  (15, @ct_rls,  'OK', NULL, '2024-10-20', NULL),
  (25, @ct_rspp, 'OK', NULL, '2026-10-04', NULL)
ON DUPLICATE KEY UPDATE status=VALUES(status), issue_date=VALUES(issue_date), expiry_date=VALUES(expiry_date), notes=VALUES(notes);
/* ============================================
   FINE POPOLAMENTO DELLE CERTIFICAZIONI
   ============================================ */


/* ============================================
  gestione notifiche tramite mail
   ============================================ */
   CREATE TABLE IF NOT EXISTS notification_log (
  id BIGINT PRIMARY KEY AUTO_INCREMENT,
  event_code   VARCHAR(100) NOT NULL,      -- es: 'EXPIRY_REMINDER_LOGIN'
  ref_date     DATE NOT NULL,              -- data di riferimento (oggi)
  sent_to      VARCHAR(200) NOT NULL,      -- destinatario
  payload_hash CHAR(64) NOT NULL,          -- sha256 contenuto
  created_at   TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE KEY uq_event_once (event_code, ref_date, sent_to, payload_hash)
);

INSERT INTO operators (first_name, last_name, email, user_password, role, active)
VALUES ('UTENTE','PRODUZIONE','produzione@plaxpackaging.it',
        '$2b$12$L5bbr4Ob6Y6vtxmvuyjSyeMnHjB/ZG5aP1e/GA1LOV0sFe8KEl/Za', --plaxG
        'HR', 1)
ON DUPLICATE KEY UPDATE
  user_password = VALUES(user_password),
  active = 1;


ALTER TABLE operator_certifications
  ADD COLUMN file_path VARCHAR(255) NULL AFTER notes;


CREATE TABLE IF NOT EXISTS company_documents (
  id INT AUTO_INCREMENT PRIMARY KEY,
  title VARCHAR(200) NOT NULL,
  year INT NOT NULL,
  category VARCHAR(100) NOT NULL,
  frequency VARCHAR(30) NOT NULL, -- es: 'annuale','semestrale','mensile','una_tantum'
  notes VARCHAR(255) NULL,
  file_path VARCHAR(500) NULL,
  created_at DATETIME NOT NULL,
  updated_at DATETIME NOT NULL,
  KEY ix_year (year),
  KEY ix_category (category),
  KEY ix_frequency (frequency)
);

-- ==========================================================
-- 0) Disattiva temporaneamente SQL_SAFE_UPDATES
-- ==========================================================
SET @OLD_SQL_SAFE_UPDATES := @@SQL_SAFE_UPDATES;
SET SQL_SAFE_UPDATES = 0;

-- ==========================================================
-- 1) Tabella categorie documenti aziendali
-- ==========================================================
CREATE TABLE IF NOT EXISTS company_doc_categories (
  code       VARCHAR(40) PRIMARY KEY,
  label      VARCHAR(200) NOT NULL,
  active     TINYINT(1) NOT NULL DEFAULT 1,
  sort_order INT NOT NULL DEFAULT 0,
  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Seed / aggiorna categorie standard
INSERT INTO company_doc_categories (code, label, active, sort_order) VALUES
  ('INF_GEN',      'INFORMAZIONI GENERALI',                     1, 10),
  ('NOMINE',       'NOMINE',                                    1, 20),
  ('FORM_ADESTR',  'FORMAZIONE ED ADDESTRAMENTO',               1, 30),
  ('VAL_RISCHI',   'VALUTAZIONE DEI RISCHI',                    1, 40),
  ('APPALTI',      'GESTIONE APPALTI',                          1, 50),
  ('IMPIANTI_MAC', 'IMPIANTI E MACCHINARI',                     1, 60),
  ('EMERGENZA',    'EMERGENZA',                                 1, 70),
  ('SORV_SAN',     'SORVEGLIANZA SANITARIA',                    1, 80),
  ('VARIE',        'VARIE',                                     1, 90)
ON DUPLICATE KEY UPDATE
  label      = VALUES(label),
  active     = VALUES(active),
  sort_order = VALUES(sort_order);


INSERT INTO company_doc_categories (code, label, active, sort_order) VALUES
  ('MODULI',      'MODULI DA COMPILARE',                     1, 100)
ON DUPLICATE KEY UPDATE
  label      = VALUES(label),
  active     = VALUES(active),
  sort_order = VALUES(sort_order);

INSERT INTO archivio.company_doc_categories (code, label, active, sort_order) VALUES
  ('INQ',      'INQUADRAMENTO AZIENDA',                     1, 110)
ON DUPLICATE KEY UPDATE
  label      = VALUES(label),
  active     = VALUES(active),
  sort_order = VALUES(sort_order);  

  INSERT INTO archivio.company_doc_categories (code, label, active, sort_order) VALUES
  ('AMB', 'DOCUMENTI GENERALI AMBIENTE', 1, 120)
ON DUPLICATE KEY UPDATE
  label = VALUES(label),
  active = VALUES(active),
  sort_order = VALUES(sort_order);

INSERT INTO archivio.company_doc_categories (code, label, active, sort_order) VALUES
  ('IDR', 'APPROVVIGIONAMENTO E SCARICHI IDRICO', 1, 130)
ON DUPLICATE KEY UPDATE
  label = VALUES(label),
  active = VALUES(active),
  sort_order = VALUES(sort_order);

INSERT INTO archivio.company_doc_categories (code, label, active, sort_order) VALUES
  ('ATM', 'EMISSIONI IN ATMOSFERA', 1, 140)
ON DUPLICATE KEY UPDATE
  label = VALUES(label),
  active = VALUES(active),
  sort_order = VALUES(sort_order);

INSERT INTO archivio.company_doc_categories (code, label, active, sort_order) VALUES
  ('SAS', 'SUOLO, SOTTOSUOLO E ACQUE SOTTERRANEE', 1, 150)
ON DUPLICATE KEY UPDATE
  label = VALUES(label),
  active = VALUES(active),
  sort_order = VALUES(sort_order);

INSERT INTO archivio.company_doc_categories (code, label, active, sort_order) VALUES
  ('RIF', 'RIFIUTI', 1, 160)
ON DUPLICATE KEY UPDATE
  label = VALUES(label),
  active = VALUES(active),
  sort_order = VALUES(sort_order);

INSERT INTO archivio.company_doc_categories (code, label, active, sort_order) VALUES
  ('LEG', 'LEGALE', 1, 170)
ON DUPLICATE KEY UPDATE
  label = VALUES(label),
  active = VALUES(active),
  sort_order = VALUES(sort_order);

  INSERT INTO archivio.company_doc_categories (code, label, active, sort_order) VALUES
  ('ASS', 'ASSICURAZIONI', 1, 180)
ON DUPLICATE KEY UPDATE
  label = VALUES(label),
  active = VALUES(active),
  sort_order = VALUES(sort_order);

INSERT INTO archivio.company_doc_categories (code, label, active, sort_order) VALUES
  ('QUAL', 'QUALITA', 1, 190)
ON DUPLICATE KEY UPDATE
  label = VALUES(label),
  active = VALUES(active),
  sort_order = VALUES(sort_order);

-- ==========================================================
-- 2) Normalizzazione valori già presenti in company_documents.category
-- ==========================================================

-- Togli spazi iniziali/finali
UPDATE company_documents
SET category = TRIM(category)
WHERE category IS NOT NULL;

-- Porta tutto in maiuscolo per facilitare i match testuali
UPDATE company_documents
SET category = UPPER(category)
WHERE category IS NOT NULL AND category <> UPPER(category);

-- ==========================================================
-- 3) Mappatura testuale → codici ufficiali
--    (adatta questi IN() se hai usato nomi diversi)
-- ==========================================================

-- INFORMAZIONI GENERALI
UPDATE company_documents
SET category = 'INF_GEN'
WHERE category IN (
  'INFORMAZIONI GENERALI',
  'INFO GENERALI',
  'INFORMAZIONI GENERALI PLAX',
  'INF_GEN'
);

-- NOMINE
UPDATE company_documents
SET category = 'NOMINE'
WHERE category IN (
  'NOMINE',
  'NOMINE VARIE'
);

-- FORMAZIONE ED ADDESTRAMENTO
UPDATE company_documents
SET category = 'FORM_ADESTR'
WHERE category IN (
  'FORMAZIONE ED ADDESTRAMENTO',
  'FORMAZIONE',
  'ADDESTRAMENTO',
  'FORMAZIONE/ADDESTRAMENTO'
);

-- VALUTAZIONE DEI RISCHI
UPDATE company_documents
SET category = 'VAL_RISCHI'
WHERE category IN (
  'VALUTAZIONE DEI RISCHI',
  'DOCUMENTO VALUTAZIONE RISCHI',
  'DVR',
  'VAL_RISCHI'
);

-- GESTIONE APPALTI
UPDATE company_documents
SET category = 'APPALTI'
WHERE category IN (
  'GESTIONE APPALTI',
  'APPALTI',
  'APPALTI E CONTRATTI'
);

-- IMPIANTI E MACCHINARI
UPDATE company_documents
SET category = 'IMPIANTI_MAC'
WHERE category IN (
  'IMPIANTI E MACCHINARI',
  'IMPIANTI',
  'MACCHINARI',
  'IMPIANTI/MACCHINARI'
);

-- EMERGENZA
UPDATE company_documents
SET category = 'EMERGENZA'
WHERE category IN (
  'EMERGENZA',
  'GESTIONE EMERGENZE',
  'PIANO EMERGENZA'
);

-- SORVEGLIANZA SANITARIA
UPDATE company_documents
SET category = 'SORV_SAN'
WHERE category IN (
  'SORVEGLIANZA SANITARIA',
  'SORV_SAN',
  'VISITE MEDICHE',
  'SANITARIA'
);

-- SORVEGLIANZA SANITARIA
UPDATE company_documents
SET category = 'SORV_SAN'
WHERE category IN (
  'SORVEGLIANZA SANITARIA',
  'SORV_SAN',
  'VISITE MEDICHE',
  'SANITARIA'
);

-- ==========================================================
-- 4) Tutto ciò che non mappa a una categoria valida → VARIE
-- ==========================================================

UPDATE company_documents cd
LEFT JOIN company_doc_categories c
       ON cd.category = c.code
SET cd.category = 'VARIE'
WHERE c.code IS NULL
   OR cd.category IS NULL
   OR cd.category = '';

-- ==========================================================
-- 5) Allinea definizione colonna + aggiungi vincolo FK
-- ==========================================================

-- Stringi la colonna alla stessa dimensione del codice (40)
ALTER TABLE company_documents
  MODIFY category VARCHAR(40) NOT NULL;

-- Se esiste già una FK con lo stesso nome, eliminala (idempotente)
SET @fk_exists := (
  SELECT COUNT(*)
  FROM INFORMATION_SCHEMA.TABLE_CONSTRAINTS
  WHERE TABLE_SCHEMA = DATABASE()
    AND TABLE_NAME = 'company_documents'
    AND CONSTRAINT_NAME = 'fk_company_docs_category'
    AND CONSTRAINT_TYPE = 'FOREIGN KEY'
);

SET @sql_drop_fk := IF(@fk_exists > 0,
  'ALTER TABLE company_documents DROP FOREIGN KEY fk_company_docs_category',
  'SELECT 1'
);
PREPARE stmt FROM @sql_drop_fk; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- Aggiungi la foreign key
ALTER TABLE company_documents
  ADD CONSTRAINT fk_company_docs_category
    FOREIGN KEY (category) REFERENCES company_doc_categories(code);

-- ==========================================================
-- 6) Ripristina SQL_SAFE_UPDATES
-- ==========================================================
SET SQL_SAFE_UPDATES = @OLD_SQL_SAFE_UPDATES;

-- 


-- job_title (mansione descrittiva)
SET @sql := (
  SELECT IF(
    EXISTS(
      SELECT 1
      FROM INFORMATION_SCHEMA.COLUMNS
      WHERE TABLE_SCHEMA = DATABASE()
        AND TABLE_NAME = 'operators'
        AND COLUMN_NAME = 'job_title'
    ),
    'SELECT 1',
    'ALTER TABLE operators
       ADD COLUMN job_title VARCHAR(120) NULL COMMENT ''Mansione descrittiva'''
  )
);
PREPARE stmt FROM @sql; EXECUTE stmt; DEALLOCATE PREPARE stmt;

-- ==========================================================
-- PATCH "NO BREAK" — Scadenze documenti aziendali
-- Obiettivo: aggiungere gestione scadenze SENZA rompere il programma
-- Assunzioni: sei già dentro al DB corretto (USE plax;)
-- ==========================================================

USE plax;

-- ----------------------------------------------------------
-- 1) HARDEN company_documents (retro-compatibile)
--    Evita insert falliti se il programma non passa created_at/updated_at
-- ----------------------------------------------------------
ALTER TABLE company_documents
  MODIFY created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  MODIFY updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP;

-- ----------------------------------------------------------
-- 2) Tabella regole scadenze (NUOVA, non rompe nulla)
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS company_document_deadline_rules (
  id INT AUTO_INCREMENT PRIMARY KEY,

  category_code VARCHAR(40) NOT NULL,
  document_name VARCHAR(255) NOT NULL,

  expiry_years DECIMAL(6,2) NOT NULL
    COMMENT 'Years. Examples: 0 (event), 0.50 (6 months), 1, 2, 3, 5, 15',

  trigger_event ENUM('PERIODIC','NEW_EMPLOYEE','ON_DEMAND') NOT NULL DEFAULT 'PERIODIC'
    COMMENT 'PERIODIC=time-based; NEW_EMPLOYEE=on hire; ON_DEMAND=manual',

  description TEXT NOT NULL,

  is_active TINYINT(1) NOT NULL DEFAULT 1,

  created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

  CONSTRAINT fk_deadline_rules_category
    FOREIGN KEY (category_code)
    REFERENCES company_doc_categories(code)
    ON UPDATE CASCADE
    ON DELETE RESTRICT,

  UNIQUE KEY uq_deadline_rules (category_code, document_name),
  KEY idx_deadline_rules_category (category_code),
  KEY idx_deadline_rules_active (is_active),
  KEY idx_deadline_rules_trigger (trigger_event)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ----------------------------------------------------------
-- 3) Link opzionale da documenti reali -> regola (NULLABLE)
--    Non rompe nulla: il tuo programma può continuare a ignorarlo
-- ----------------------------------------------------------
ALTER TABLE company_documents
  ADD COLUMN deadline_rule_id INT NULL AFTER category;

CREATE INDEX idx_company_documents_deadline_rule
  ON company_documents (deadline_rule_id);

ALTER TABLE company_documents
  ADD CONSTRAINT fk_company_documents_deadline_rule
    FOREIGN KEY (deadline_rule_id)
    REFERENCES company_document_deadline_rules(id)
    ON UPDATE CASCADE
    ON DELETE SET NULL;

-- ----------------------------------------------------------
-- 4) Campi opzionali per scheduler (NULLABLE)
--    reference_date: data da cui parte la scadenza
--    next_due_date: prossima scadenza calcolata
-- ----------------------------------------------------------
ALTER TABLE company_documents
  ADD COLUMN reference_date DATE NULL AFTER year,
  ADD COLUMN next_due_date DATE NULL AFTER reference_date;

CREATE INDEX idx_company_documents_next_due
  ON company_documents (next_due_date);

-- ----------------------------------------------------------
-- 5) (FACOLTATIVO) Query di calcolo next_due_date
--    Da eseguire quando:
--      - deadline_rule_id è valorizzato
--      - reference_date è valorizzata
--    Nota: gestisce 0.50 anni come 6 mesi
-- ----------------------------------------------------------
/*
UPDATE company_documents d
JOIN company_document_deadline_rules r ON r.id = d.deadline_rule_id
SET d.next_due_date = CASE
  WHEN r.expiry_years = 0 THEN NULL
  WHEN r.expiry_years = 0.50 THEN DATE_ADD(d.reference_date, INTERVAL 6 MONTH)
  ELSE DATE_ADD(d.reference_date, INTERVAL ROUND(r.expiry_years * 12) MONTH)
END
WHERE d.deadline_rule_id IS NOT NULL
  AND d.reference_date IS NOT NULL;
*/
USE plax;

INSERT INTO company_document_deadline_rules
(category_code, document_name, expiry_years, trigger_event, description)
VALUES

-- =========================
-- AMBIENTE
-- =========================
('AMB','Autorizzazione AUA / AIA',15,'PERIODIC',
 'Autorizzazione unica ambientale per emissioni, scarichi e rifiuti; validità 15 anni salvo modifiche impiantistiche.'),

-- =========================
-- APPALTI
-- =========================
('APPALTI','Elenco aziende appaltatrici',1,'PERIODIC',
 'Aggiornamento annuale delle imprese che operano in sito per gestione DUVRI e idoneità tecnico-professionale.'),

('APPALTI','Verifica idoneità tecnico-professionale',1,'PERIODIC',
 'Controllo annuale dei requisiti di sicurezza delle ditte appaltatrici ai sensi dell’art. 26 D.Lgs. 81/08.'),

-- =========================
-- EMERGENZA
-- =========================
('EMERGENZA','Controlli antincendio interni',1,'PERIODIC',
 'Verifica documentata delle misure di prevenzione incendi e gestione emergenze ai sensi del DPR 151/2011.'),

('EMERGENZA','CPI / SCIA antincendio',5,'PERIODIC',
 'Certificato Prevenzione Incendi o SCIA antincendio con rinnovo quinquennale.'),

('EMERGENZA','Formazione addetti antincendio',5,'PERIODIC',
 'Formazione e aggiornamento quinquennale degli addetti antincendio.'),

('EMERGENZA','Prova di evacuazione',0.50,'PERIODIC',
 'Esecuzione e registrazione della prova di evacuazione aziendale con verbale; cadenza almeno semestrale.'),

-- =========================
-- EMISSIONI ATMOSFERA
-- =========================
('ATM','Riesame descrizione emissioni',1,'PERIODIC',
 'Verifica annuale dei punti di emissione, sostanze emesse e quantità autorizzate.'),

('ATM','Autorizzazione emissioni in atmosfera',15,'PERIODIC',
 'Autorizzazione ex art. 269/281 D.Lgs. 152/06; validità massima 15 anni.'),

('ATM','Analisi annuali emissioni convogliate',1,'PERIODIC',
 'Misure analitiche annuali dei parametri emissivi previste dall’autorizzazione.'),

('ATM','Piano gestione solventi',1,'PERIODIC',
 'Documento obbligatorio VOC con verifica annuale consumi e bilancio solventi.'),

('ATM','Verifica efficienza centrale termica',2,'PERIODIC',
 'Controllo biennale dell’efficienza energetica ai sensi del DPR 74/2013.'),

-- =========================
-- FORMAZIONE / NUOVO DIPENDENTE
-- =========================
('FORM_ADESTR','Informazione sui rischi (nuovo dipendente)',0,'NEW_EMPLOYEE',
 'Consegna informazioni su rischi, emergenze e figure della sicurezza con firma.'),

('FORM_ADESTR','Formazione generale sicurezza (nuovo dipendente)',0,'NEW_EMPLOYEE',
 'Formazione obbligatoria di base sicurezza prima dell’operatività.'),

('FORM_ADESTR','Formazione specifica mansione (nuovo dipendente)',0,'NEW_EMPLOYEE',
 'Formazione sui rischi specifici della mansione assegnata.'),

('FORM_ADESTR','Addestramento pratico operativo (nuovo dipendente)',0,'NEW_EMPLOYEE',
 'Addestramento pratico documentato su macchine e procedure.'),

('FORM_ADESTR','Consegna e registrazione DPI (nuovo dipendente)',0,'NEW_EMPLOYEE',
 'Assegnazione DPI adeguati e firma di presa in carico.'),

('FORM_ADESTR','Inserimento in sorveglianza sanitaria (nuovo dipendente)',0,'NEW_EMPLOYEE',
 'Inserimento nel protocollo sanitario e pianificazione visite.'),

('FORM_ADESTR','Giudizio di idoneità alla mansione (nuovo dipendente)',0,'NEW_EMPLOYEE',
 'Giudizio del Medico Competente per mansioni soggette a sorveglianza sanitaria.'),

('FORM_ADESTR','Aggiornamento elenco dipendenti e mansioni (nuovo dipendente)',0,'NEW_EMPLOYEE',
 'Aggiornamento anagrafica aziendale, mansione e reparto.'),

('FORM_ADESTR','Verifica impatto su DVR e valutazioni rischi (nuovo dipendente)',0,'NEW_EMPLOYEE',
 'Verifica introduzione di nuovi rischi o esposizioni non valutate.'),

('FORM_ADESTR','Informazione su procedure di emergenza (nuovo dipendente)',0,'NEW_EMPLOYEE',
 'Illustrazione vie di esodo, punti di raccolta e comportamenti in emergenza.'),

-- =========================
-- RIFIUTI
-- =========================
('RIF','Riesame produzione rifiuti',1,'PERIODIC',
 'Verifica annuale tipologie, codici CER e quantità prodotte.'),

('RIF','Iscrizione Albo Gestori Ambientali',5,'PERIODIC',
 'Iscrizione per trasporto o stoccaggio rifiuti; validità quinquennale.'),

('RIF','MUD – dichiarazione annuale',1,'PERIODIC',
 'Comunicazione annuale dei rifiuti prodotti alle Camere di Commercio.'),

-- =========================
-- IMPIANTI E MACCHINARI
-- =========================
('IMPIANTI_MAC','Verifica apparecchi a pressione (PED)',1,'PERIODIC',
 'Verifica periodica annuale delle apparecchiature in pressione.'),

('IMPIANTI_MAC','Verifica macchine di sollevamento',1,'PERIODIC',
 'Verifica annuale dell’integrità strutturale e dei dispositivi di sicurezza.'),

('IMPIANTI_MAC','Verifica messa a terra – luoghi ordinari',2,'PERIODIC',
 'Verifica periodica impianto di terra ai sensi del DPR 462/01.'),

('IMPIANTI_MAC','Verifica messa a terra – luoghi speciali',5,'PERIODIC',
 'Verifica quinquennale impianto di terra in ambienti a maggior rischio.'),

('IMPIANTI_MAC','Manutenzione e verifica linea vita copertura',1,'PERIODIC',
 'Ispezione e manutenzione annuale del sistema anticaduta con verbale.'),

('IMPIANTI_MAC','Programma manutenzioni',1,'PERIODIC',
 'Piano annuale degli interventi di manutenzione preventiva e correttiva.'),

-- =========================
-- INQUADRAMENTO AZIENDA
-- =========================
('INQ','Visura camerale',1,'PERIODIC',
 'Documento camerale aggiornato annualmente.'),

('INQ','Elenco sostanze chimiche',1,'PERIODIC',
 'Inventario sostanze chimiche e SDS aggiornato.'),

-- =========================
-- NOMINE
-- =========================
('NOMINE','Elezione RLS',3,'PERIODIC',
 'Rinnovo della carica RLS secondo accordi applicati.'),

('NOMINE','Nomina addetti emergenza incendio',5,'PERIODIC',
 'Nomina addetti emergenza con requisito formativo quinquennale.'),

('NOMINE','Nomina addetti primo soccorso',3,'PERIODIC',
 'Nomina addetti primo soccorso con aggiornamento triennale.'),

-- =========================
-- IDRICO
-- =========================
('IDR','Riesame scarichi idrici',1,'PERIODIC',
 'Verifica annuale dei punti di scarico e limiti autorizzativi.'),

('IDR','Autorizzazione scarichi reflui',4,'PERIODIC',
 'Autorizzazione allo scarico reflui con validità quadriennale.'),

('IDR','Analisi acque reflue',1,'PERIODIC',
 'Analisi annuali dei reflui industriali.'),

-- =========================
-- SORVEGLIANZA SANITARIA
-- =========================
('SORV_SAN','Giudizi di idoneità',1,'PERIODIC',
 'Visite periodiche dei lavoratori secondo protocollo sanitario.'),

-- =========================
-- SUOLO / SOTTOSUOLO
-- =========================
('SAS','Riesame procedure suolo e sottosuolo',1,'PERIODIC',
 'Verifica annuale delle procedure di prevenzione contaminazioni.'),

-- =========================
-- VALUTAZIONE DEI RISCHI
-- =========================
('VAL_RISCHI','Documento di Valutazione dei Rischi (DVR)',3,'PERIODIC',
 'Riesame triennale del DVR con aggiornamenti immediati in caso di variazioni.'),

('VAL_RISCHI','Valutazione rischio chimico',3,'PERIODIC','Riesame triennale.'),
('VAL_RISCHI','Valutazione rischio cancerogeni',3,'PERIODIC','Riesame triennale.'),
('VAL_RISCHI','Valutazione rischio biologico',3,'PERIODIC','Riesame triennale.'),
('VAL_RISCHI','Valutazione rischio rumore',3,'PERIODIC','Riesame triennale.'),
('VAL_RISCHI','Valutazione vibrazioni',3,'PERIODIC','Riesame triennale.'),
('VAL_RISCHI','Movimentazione manuale carichi',3,'PERIODIC','Riesame triennale.'),
('VAL_RISCHI','Movimenti ripetitivi arto superiore',3,'PERIODIC','Riesame triennale.'),
('VAL_RISCHI','Rischio incendio',3,'PERIODIC','Riesame triennale.'),
('VAL_RISCHI','ATEX',3,'PERIODIC','Riesame triennale.'),
('VAL_RISCHI','VDT',3,'PERIODIC','Riesame triennale.'),
('VAL_RISCHI','Rischi minori e apprendisti',3,'PERIODIC','Riesame triennale.'),
('VAL_RISCHI','Stress lavoro-correlato',3,'PERIODIC','Riesame triennale.'),
('VAL_RISCHI','Rischi interferenziali',3,'PERIODIC','Riesame triennale.'),
('VAL_RISCHI','Rischio fulminazione',3,'PERIODIC','Riesame triennale.'),
('VAL_RISCHI','Spazi confinati',3,'PERIODIC','Riesame triennale.'),
('VAL_RISCHI','Lavori in quota',3,'PERIODIC','Riesame triennale.'),
('VAL_RISCHI','Rischio sismico',3,'PERIODIC','Riesame triennale.'),
('VAL_RISCHI','Agenti fisici vari',3,'PERIODIC','Riesame triennale.'),

-- =========================
-- VARIE / CERTIFICAZIONI
-- =========================
('VARIE','Certificazione ISO 45001',3,'PERIODIC','Certificazione salute e sicurezza sul lavoro.'),
('VARIE','Certificazione ISO 9001',3,'PERIODIC','Certificazione sistema qualità.'),
('VARIE','Certificazione ISO 14001',3,'PERIODIC','Certificazione sistema ambientale.'),
('VARIE','Audit di sorveglianza ISO',1,'PERIODIC','Audit annuale dell’ente di certificazione.'),

-- =========================
-- IMPIANTI SPECIALI
-- =========================
('IMPIANTI_MAC','Verifica annuale carrelli elevatori',1,'PERIODIC',
 'Controllo periodico documentato del carrello elevatore.'),

('IMPIANTI_MAC','Controllo perdite F-GAS',1,'PERIODIC',
 'Verifica annuale impianti con gas fluorurati sopra soglia.'),

('IMPIANTI_MAC','Registro apparecchiature F-GAS',1,'PERIODIC',
 'Aggiornamento annuale del registro F-GAS.');
