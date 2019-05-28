-- Tabela plezalisc:
CREATE TABLE plezalisca (
  id serial PRIMARY KEY,
  ime text NOT NULL,
  drzava text NOT NULL,
  st_smeri integer,
  razpon_ocen text,
  najlazja text,
  najtezja text
);

-- Tabela smeri:
CREATE TABLE smeri (
  id serial PRIMARY KEY,
  ime text NOT NULL,
  plezalisce text,
  ocena text,
  dolzina text
);

-- Tabela regij in plezalisc:
CREATE TABLE regije (
  id serial PRIMARY KEY,
  plezalisce text NOT NULL,
  regija text,
  drzava text NOT NULL
)
