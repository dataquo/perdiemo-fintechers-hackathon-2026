---
title: "KB_Challenge_Back-office_document_controls"
original_file: "KB_Challenge_Back-office_document_controls.docx"
converted_at: "2026-10-19T19:12:56.840Z"
---


| HACKATHON CHALLENGEAutomatizace dokumentových kontrol v back-officeOd příchozí dokumentace k auditovatelnému výsledku a řízení výjimek | TRACK 4/6 |
| --- | --- |



| HLAVNÍ OTÁZKA:  Dokáže AI agent převzít různorodou sadu back-office dokumentů, rozpoznat jejich typ, vytěžit klíčové údaje, ověřit úplnost a konzistenci a předat člověku pouze výjimky, aniž by ztratil auditní stopu? |
| --- |



| KONTEXT A CÍL VÝZVY / OČEKÁVANÝ PROTOTYP<br>Back-office týmy dnes ručně kontrolují dokumenty, porovnávají údaje mezi podklady a řeší chybějící nebo nejednoznačné informace. Cílem je vytvořit obecně použitelné řešení, které zrychlí kontrolu, zvýší její konzistenci a vytvoří dohledatelný kontrolní protokol. AI výstup je podkladem pro rozhodnutí, nikoli automatickým finálním schválením.<br>• Přijme balíček dokumentů k obchodnímu případu.<br>• Ověří úplnost sady dokumentů (cca 5–7 různých dokumentů = sada vždy stanovena v dokumentu Smlouva). Tj. dokumenty klasifikuje a následně vytěží předem definované atributy dle typu dokumentu, včetně míry jistoty.<br>• V případě neúplnosti / některých specifických nekonzistencí automaticky triggeruje požadavek na klienta pro doplnění / opravu.<br>• Rozdělí výsledky na úspěšné kontroly, nesrovnalosti, upozornění a manuální posouzení a vygeneruje citovaný a auditovatelný protokol s doporučeným následným krokem pro pracovníka back-office. | TECHNICKÉ ÚKOLY PRO TÝMY<br>• Ingesce a preprocessing: načtení PDF/obrázků, OCR a zachování vazby na původní stránku.<br>• Klasifikace: určení typu dokumentu; bonus za rozdělení vícedokumentového PDF a přeházených stran.<br>• Extrakce: strukturovaný výstup atributů, zdrojová citace a confidence score.<br>• Rules engine: konfigurovatelné kontroly úplnosti, shody a logických vazeb.<br>• Human-in-the-loop (HITL): potvrzení, úprava, zamítnutí nebo vrácení výsledku k doplnění.<br>• Audit trail: verze vstupů, použité pravidlo/model, čas běhu a historie lidských zásahů. |  |
| --- | --- | --- |
| DEMO SCÉNÁŘ<br>• Happy path: kompletní sada projde a vznikne protokol.<br>• Error path: chybí dokument nebo chybí- neshoduje se klíčový údaj.<br>• Automatické řešení/HITL next steps | HODNOCENÍ<br>• Přesnost klasifikace, extrakce a kontrol.<br>• Dohledatelnost důkazů a vysvětlitelnost.<br>• Robustnost vůči kvalitě a variantám dokumentů.<br>• Reálná použitelnost pro back-office. | MANTINELY<br>• Pravidla musí být oddělena od extrakce a snadno měnitelná.<br>• Kontinuální zlepšování – zpřesňování pravidel dle reálných rozhodnutí. |


