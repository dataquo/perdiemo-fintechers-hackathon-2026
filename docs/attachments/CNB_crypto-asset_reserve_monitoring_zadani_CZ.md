---
title: "CNB_crypto-asset_reserve_monitoring_zadani_CZ"
original_file: "CNB_crypto-asset_reserve_monitoring_zadani_CZ.md"
source_track: "Track 2 · Stablecoins and new financial infrastructure"
fetched_at: "2026-10-19T19:10:58.574Z"
---

# Zadání Hackathon Challenge: Crypto-asset reserve monitoring (Systém pro kontrolu krytí kryptoaktiv)

*Track 2 · Česká národní banka (ČNB). Originál zadání.*

1.  **Kontext a hlavní cíl výzvy:**

Cílem výzvy je vytvořit mikroobezřetnostní SupTech (Supervisory Technology) nástroj, který omezí časový nesoulad (frequency mismatch) mezi průběžnými pohyby digitálních závazků na blockchainu a periodickým vykazováním reálných rezerv. Systém má vydavateli, partnerům, zákazníkům nebo dohledovému orgánu vydavatele poskytovat automatizovaný a průběžně aktualizovaný přehled o krytí kryptoaktiv, včas identifikovat pokles pod stanovenou úroveň a podpořit stabilitu emitentů v souladu s nařízením MiCA.

Očekávaným výstupem je funkční prototyp, který propojí simulovaná on-chain a off-chain data, vypočte aktuální míru krytí, zaznamená čas a původ použitých dat a zobrazí výsledek v přehledném dashboardu. Tým současně popíše architekturu řešení, datový model, použité předpoklady, způsob zabezpečení rozhraní a postup ověření správnosti výpočtů a alertů.

Řešení bude hodnoceno podle správnosti a auditovatelnosti výpočtu krytí, schopnosti pracovat s rozdílnou frekvencí vstupních dat, kvality identifikace a signalizace rizik, bezpečnosti integračních rozhraní, srozumitelnosti dashboardu a možnosti rozšířit prototyp z EMT na ART.

2.  **Fáze 1: EMT (Tokeny elektronických peněz) -- Kontrola likvidity 1:1**

Tato fáze se zaměřuje na stablecoiny, jejichž hodnota je pevně navázána na jedinou fiat měnu (např. EUR, CZK, USD). Emitent podléhá extrémně přísným požadavkům na denní sledování potřeby likvidity a povinnost zajistit 100% krytí rezervami.

**Technické úkoly pro soutěžící týmy:**

-   **Agregace on-chain závazků:** Naprogramovat integrační vrstvu, která se v konfigurovatelných intervalech dotazuje API veřejných blockchainových průzkumníků, například Etherscan, na objem tokenů v oběhu. U každého načtení musí systém zaznamenat zdroj, čas získání dat, identifikátor sítě a stav úspěšnosti dotazu, aby bylo možné posoudit aktuálnost a úplnost výsledku.

-   **Unifikace identifikátorů:** Namísto kódů ISIN využít pro přesnou identifikaci tokenů napříč různými DLT sítěmi metodiku DTI (Digital Token Identifier).

-   **Sběr off-chain aktiv:** Vytvořit REST API endpoint, který bude simulovat bezpečný příjem dat o aktuálních zůstatcích z chráněných účtů depozitních komerčních bank.

-   **Asimilační engine:** Navrhnout databázový model a výpočetní vrstvu, například s využitím PostgreSQL a Pythonu, které propojí okamžitá data z blockchainu s periodickými daty z bank. Výstup musí rozlišovat čas poslední aktualizace obou zdrojů, vypočtenou míru krytí a informaci o tom, zda je výsledek založen na dostatečně aktuálních datech.

-   **Krizový alerting:** Vytvořit exekutivní dashboard s automatizovaným spouštěčem, který vyhlásí poplach, pokud vypočtená míra krytí klesne pod úroveň 1:1. Alert musí zobrazit zjištěnou hodnotu, čas výpočtu, aktuálnost použitých vstupů a zdroj odchylky, pokud jej lze určit.

3.  **Fáze 2: ART (Tokeny vázané na aktiva) -- Dynamické oceňování portfolia**

Tato fáze rozšiřuje systém na kryptoaktiva, jejichž hodnota je stabilizována odkazem na koš aktiv, komodity, více fiat měn nebo jiná kryptoaktiva. Samotný vydaný token nesmí vykazovat znaky finančního nástroje podle zákona o podnikání na kapitálovém trhu (ZPKT), například cenného papíru, derivátu nebo podílového listu nesoucího úrok. Rezervní aktiva je proto nutné posuzovat odděleně: systém má sledovat jejich složení, ocenění, likviditu a rizikovost jako portfolio kryjící vydané tokeny.

**Definice validních rezervních aktiv (pro algoritmické sledování):**

1.  **Vysoce likvidní finanční nástroje:** Krátkodobé státní dluhopisy (v souladu se standardy pro fondy peněžního trhu -- MMF) s minimálním kreditním a tržním rizikem.

2.  **Komodity:** Fyzicky alokované drahé kovy (např. zlato s doložitelnou úschovou u licencovaného depozitáře).

3.  **Diverzifikovaná fiat aktiva:** Vklady ve více stabilních měnách rozložené mezi různé úvěrové instituce pro minimalizaci koncentračního rizika.

4.  **Referenční kryptoaktiva:** Jiná vysoce likvidní kryptoaktiva (on-chain kolaterál) s transparentně dohledatelnou strukturou na blockchainu.

**Technické úkoly pro soutěžící týmy:**

-   **Granulární datový model:** Rozšířit databázi z Fáze 1 o hierarchii podtříd aktiv (sub-asset classes) pro uložení detailních atributů, jako je metoda ocenění, úroková sazba nebo splatnost držených dluhopisů.

-   **Integrace Oracles (Cenové feedy):** Napojit systém na externí poskytovatele dat pro získávání aktuálních tržních cen (mark-to-market), aby nástroj dokázal v reálném čase přeceňovat kolísavou hodnotu držených komodit a dluhopisů.

-   **Volitelné -- validace kapitálových požadavků:** Rozšířit kontrolní mechanismus o výpočet vlastních zdrojů emitenta. Systém musí umožnit nastavit a doložit použité regulatorní pravidlo a ověřit, zda emitent disponuje kapitálem ve výši nejméně 350 000 EUR, případně kapitálem určeným stanoveným procentuálním podílem z rezervních aktiv podle nařízení MiCA.

-   **Volitelné -- hodnocení kvality aktiv:** Implementovat do dashboardu regulatorní štítky, které zařadí držená aktiva podle jejich likvidity a rizika. U každého štítku musí být dohledatelné použité vstupní údaje a pravidlo, podle něhož bylo hodnocení přiděleno; například fiat vklady mohou být hodnoceny výše než firemní dluh, pokud to odpovídá nastaveným kritériím.
