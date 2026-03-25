# diagnosticos_db.py
# Fuente: CIE-10 Vol.1 2018 (OPS/OMS) extraído directamente del PDF oficial
# + CIE-11 equivalencias (OMS, icd.who.int / Guía Feb.2023)
# Sin DSM — solo CIE-10 y CIE-11 como solicitado

DIAGNOSTICOS = [
    # ─────────────────────────────────────────────────────
    # CAP A-B · ENFERMEDADES INFECCIOSAS Y PARASITARIAS
    # ─────────────────────────────────────────────────────
    {"cie10":"A09","cie11":"1A40","nombre":"Diarrea y gastroenteritis de presunto origen infeccioso","cap":"A-B · Infeccioso","tags":["diarrea","gastroenteritis","infección intestinal","diarrea aguda"]},
    {"cie10":"A15","cie11":"1B10","nombre":"Tuberculosis respiratoria","cap":"A-B · Infeccioso","tags":["tuberculosis","TBC","Koch","pulmón","mycobacterium"]},
    {"cie10":"A41","cie11":"1G40","nombre":"Otras sepsis","cap":"A-B · Infeccioso","tags":["sepsis","septicemia","bacteriemia","shock séptico"]},
    {"cie10":"A50","cie11":"1A62","nombre":"Sífilis congénita","cap":"A-B · Infeccioso","tags":["sífilis congénita","treponema"]},
    {"cie10":"A51","cie11":"1A60","nombre":"Sífilis precoz","cap":"A-B · Infeccioso","tags":["sífilis","treponema","ITS","infección de transmisión sexual"]},
    {"cie10":"A53","cie11":"1A60.Z","nombre":"Otras sífilis y las no especificadas","cap":"A-B · Infeccioso","tags":["sífilis","treponema","ITS"]},
    {"cie10":"A54","cie11":"1A70","nombre":"Infección gonocócica (gonorrea)","cap":"A-B · Infeccioso","tags":["gonorrea","gonococo","ITS","uretritis","secreción uretral"]},
    {"cie10":"A59","cie11":"1A90","nombre":"Tricomoniasis","cap":"A-B · Infeccioso","tags":["tricomoniasis","trichomonas","ITS","vaginitis"]},
    {"cie10":"A60","cie11":"1E90.1","nombre":"Infección anogenital por herpes simple","cap":"A-B · Infeccioso","tags":["herpes genital","herpes simple","ITS","VHS"]},
    {"cie10":"B20","cie11":"1C62","nombre":"Enfermedad por VIH que da lugar a enfermedades infecciosas y parasitarias","cap":"A-B · Infeccioso","tags":["VIH","HIV","SIDA","AIDS","inmunodeficiencia","antirretroviral"]},
    {"cie10":"B24","cie11":"1C62.Z","nombre":"Enfermedad por VIH no especificada","cap":"A-B · Infeccioso","tags":["VIH","HIV","SIDA"]},
    {"cie10":"B35","cie11":"1F28","nombre":"Dermatofitosis (tiña)","cap":"A-B · Infeccioso","tags":["tiña","hongos piel","tinea","dermatofitosis","micosis superficial"]},
    {"cie10":"B37","cie11":"1F23","nombre":"Candidiasis","cap":"A-B · Infeccioso","tags":["candidiasis","cándida","hongos","candida albicans","muguet"]},

    # ─────────────────────────────────────────────────────
    # CAP E · ENDOCRINO, NUTRICIONAL Y METABÓLICO
    # ─────────────────────────────────────────────────────
    {"cie10":"E03","cie11":"5A00","nombre":"Otros hipotiroidismos","cap":"E · Endocrino","tags":["hipotiroidismo","tiroides","TSH elevado","Hashimoto","cansancio tiroides","levotiroxina"]},
    {"cie10":"E05","cie11":"5A01","nombre":"Tirotoxicosis [hipertiroidismo]","cap":"E · Endocrino","tags":["hipertiroidismo","tirotoxicosis","Graves","Basedow","tiroides hiperactivo"]},
    {"cie10":"E06","cie11":"5A00","nombre":"Tiroiditis","cap":"E · Endocrino","tags":["tiroiditis","Hashimoto","tiroiditis autoinmune","tiroiditis de De Quervain"]},
    {"cie10":"E10","cie11":"5A10","nombre":"Diabetes mellitus tipo 1","cap":"E · Endocrino","tags":["DM1","diabetes tipo 1","insulinodependiente","insulina","glucosa"]},
    {"cie10":"E11","cie11":"5A11","nombre":"Diabetes mellitus tipo 2","cap":"E · Endocrino","tags":["diabetes","DM2","diabetes tipo 2","glucosa","metformina","hiperglucemia"]},
    {"cie10":"E13","cie11":"5A13","nombre":"Otras diabetes mellitus especificadas","cap":"E · Endocrino","tags":["diabetes LADA","MODY","diabetes secundaria"]},
    {"cie10":"E14","cie11":"5A1Z","nombre":"Diabetes mellitus no especificada","cap":"E · Endocrino","tags":["diabetes","DM","hiperglucemia","glucosuria"]},
    {"cie10":"E21","cie11":"5A54","nombre":"Hiperparatiroidismo y otros trastornos de la paratiroides","cap":"E · Endocrino","tags":["hiperparatiroidismo","paratiroides","calcio elevado","hipercalcemia"]},
    {"cie10":"E22","cie11":"5A60","nombre":"Hiperfunción de la glándula hipófisis","cap":"E · Endocrino","tags":["hiperfunción hipofisaria","acromegalia","Cushing","hiperprolactinemia"]},
    {"cie10":"E24","cie11":"5A61","nombre":"Síndrome de Cushing","cap":"E · Endocrino","tags":["Cushing","hipercortisolismo","obesidad central","cortisol"]},
    {"cie10":"E27","cie11":"5A70","nombre":"Otros trastornos de la glándula suprarrenal","cap":"E · Endocrino","tags":["suprarrenal","Addison","insuficiencia suprarrenal","cortisol bajo"]},
    {"cie10":"E66","cie11":"5B81","nombre":"Obesidad","cap":"E · Endocrino","tags":["obesidad","sobrepeso","IMC elevado","adiposidad","IMC mayor 30"]},
    {"cie10":"E78","cie11":"5C80","nombre":"Trastornos del metabolismo de las lipoproteínas y otras lipidemias","cap":"E · Endocrino","tags":["dislipidemia","colesterol","triglicéridos","hiperlipidemia","lípidos","hiperlipemia"]},
    {"cie10":"E78.0","cie11":"5C80.0","nombre":"Hipercolesterolemia pura","cap":"E · Endocrino","tags":["hipercolesterolemia","colesterol alto","LDL elevado","estatina"]},
    {"cie10":"E78.1","cie11":"5C80.1","nombre":"Hipertrigliceridemia pura","cap":"E · Endocrino","tags":["hipertrigliceridemia","triglicéridos altos","VLDL"]},
    {"cie10":"E78.5","cie11":"5C80.Z","nombre":"Hiperlipidemia mixta","cap":"E · Endocrino","tags":["hiperlipidemia mixta","colesterol y triglicéridos altos","dislipidemia mixta"]},
    {"cie10":"E83","cie11":"5C60","nombre":"Trastornos del metabolismo de los minerales","cap":"E · Endocrino","tags":["trastorno mineral","calcio","fósforo","magnesio","cobre","zinc"]},
    {"cie10":"E86","cie11":"5C70.0","nombre":"Depleción de volumen","cap":"E · Endocrino","tags":["deshidratación","depleción volumen","hipovolemia"]},
    {"cie10":"E87","cie11":"5C70","nombre":"Otros trastornos de los electrólitos y del equilibrio ácido-base","cap":"E · Endocrino","tags":["electrólitos","sodio","potasio","hiponatremia","hipocalemia","hipernatremia","acidosis","alcalosis"]},

    # ─────────────────────────────────────────────────────
    # CAP F · TRASTORNOS MENTALES Y DEL COMPORTAMIENTO
    # ─────────────────────────────────────────────────────
    # Orgánicos
    {"cie10":"F01","cie11":"6D81","nombre":"Demencia vascular","cap":"F · Mental","tags":["demencia vascular","deterioro cognitivo vascular","ACV demencia"]},
    {"cie10":"F03","cie11":"6D83","nombre":"Demencia no especificada","cap":"F · Mental","tags":["demencia","deterioro cognitivo","pérdida memoria"]},
    {"cie10":"F05","cie11":"6D70","nombre":"Delirio no inducido por alcohol ni por otras sustancias psicoactivas","cap":"F · Mental","tags":["delirium","confusión aguda","desorientación","agitación"]},
    {"cie10":"F06","cie11":"6E6Z","nombre":"Otros trastornos mentales debidos a lesión y disfunción cerebral","cap":"F · Mental","tags":["trastorno mental orgánico","orgánico","disfunción cerebral"]},
    # Cannabis
    {"cie10":"F12","cie11":"6C41","nombre":"Trastornos mentales y del comportamiento debidos al uso de cannabinoides","cap":"F · Cannabis","tags":["cannabis","marihuana","THC","CBD","cannabinoide","uso de cannabis"]},
    {"cie10":"F12.0","cie11":"6C41.0","nombre":"Intoxicación aguda por cannabinoides — Emergencia Cannábica","cap":"F · Cannabis","tags":["emergencia cannábica","intoxicación cannabis","crisis cannabinoide","reacción adversa THC","pánico cannabis","taquicardia cannabis","ansiedad cannabis","reacción adversa cannabis"]},
    {"cie10":"F12.1","cie11":"6C41.1","nombre":"Uso nocivo de cannabinoides","cap":"F · Cannabis","tags":["uso nocivo cannabis","abuso cannabis","daño cannabis"]},
    {"cie10":"F12.2","cie11":"6C41.2","nombre":"Síndrome de dependencia a cannabinoides","cap":"F · Cannabis","tags":["dependencia cannabis","adicción cannabis","CUD"]},
    {"cie10":"F12.3","cie11":"6C41.3","nombre":"Estado de abstinencia de cannabinoides","cap":"F · Cannabis","tags":["abstinencia cannabis","síndrome abstinencia THC","cese cannabis"]},
    {"cie10":"F12.5","cie11":"6C41.5","nombre":"Trastorno psicótico inducido por cannabinoides","cap":"F · Cannabis","tags":["psicosis cannabis","psicosis THC","cannabis psicosis"]},
    # Otras sustancias
    {"cie10":"F10","cie11":"6C40","nombre":"Trastornos mentales y del comportamiento debidos al uso de alcohol","cap":"F · Mental","tags":["alcohol","alcoholismo","dependencia alcohólica","AUDIT","bebida"]},
    {"cie10":"F10.1","cie11":"6C40.1","nombre":"Uso nocivo de alcohol","cap":"F · Mental","tags":["uso nocivo alcohol","abuso alcohol","daño alcohol"]},
    {"cie10":"F10.2","cie11":"6C40.2","nombre":"Síndrome de dependencia al alcohol","cap":"F · Mental","tags":["dependencia alcohólica","alcoholismo","adicción alcohol"]},
    {"cie10":"F11","cie11":"6C43","nombre":"Trastornos mentales y del comportamiento debidos al uso de opioides","cap":"F · Mental","tags":["opioides","morfina","heroína","tramadol","fentanilo","codeína","opioide"]},
    {"cie10":"F13","cie11":"6C44","nombre":"Trastornos por uso de sedantes, hipnóticos o ansiolíticos","cap":"F · Mental","tags":["benzodiacepinas","sedantes","hipnóticos","diazepam","alprazolam","clonazepam","lorazepam"]},
    {"cie10":"F14","cie11":"6C45","nombre":"Trastornos por uso de cocaína","cap":"F · Mental","tags":["cocaína","pasta base","crack","estimulante ilegal"]},
    {"cie10":"F17","cie11":"6C4A","nombre":"Trastornos mentales y del comportamiento debidos al uso de tabaco","cap":"F · Mental","tags":["tabaco","nicotina","cigarrillo","dependencia tabáquica","fumar","índice tabáquico"]},
    {"cie10":"F19","cie11":"6C4H","nombre":"Trastornos por uso de múltiples drogas y otras sustancias psicoactivas","cap":"F · Mental","tags":["politoxicomanía","múltiples sustancias","polidrogadicción"]},
    # Psicosis
    {"cie10":"F20","cie11":"6A20","nombre":"Esquizofrenia","cap":"F · Mental","tags":["esquizofrenia","psicosis","alucinaciones","delirios","antipsicótico"]},
    {"cie10":"F20.0","cie11":"6A20.0","nombre":"Esquizofrenia paranoide","cap":"F · Mental","tags":["esquizofrenia paranoide","delirios paranoides","persecución","esquizofrenia"]},
    {"cie10":"F21","cie11":"6A21","nombre":"Trastorno esquizotípico","cap":"F · Mental","tags":["esquizotípico","personalidad esquizotípica"]},
    {"cie10":"F22","cie11":"6A24","nombre":"Trastornos delirantes persistentes","cap":"F · Mental","tags":["trastorno delirante","paranoia","ideas delirantes","celotipia","erotomanía"]},
    {"cie10":"F23","cie11":"6A23","nombre":"Trastornos psicóticos agudos y transitorios","cap":"F · Mental","tags":["psicosis aguda","psicosis transitoria","brote psicótico","episodio psicótico"]},
    {"cie10":"F25","cie11":"6A25","nombre":"Trastornos esquizoafectivos","cap":"F · Mental","tags":["esquizoafectivo","bipolar psicótico","psicosis afectiva"]},
    # Trastornos del humor
    {"cie10":"F30","cie11":"6A60","nombre":"Episodio maníaco","cap":"F · Mental","tags":["manía","episodio maníaco","euforia","grandiosidad","hiperactividad maníaca"]},
    {"cie10":"F31","cie11":"6A60","nombre":"Trastorno afectivo bipolar","cap":"F · Mental","tags":["bipolar","trastorno bipolar","manía","depresión bipolar","ciclotimia"]},
    {"cie10":"F31.0","cie11":"6A60.0","nombre":"Trastorno bipolar, episodio maníaco actual sin síntomas psicóticos","cap":"F · Mental","tags":["bipolar maníaco","manía","hipomanía","euforia patológica"]},
    {"cie10":"F31.3","cie11":"6A60.3","nombre":"Trastorno bipolar, episodio depresivo moderado o leve actual","cap":"F · Mental","tags":["bipolar depresivo","depresión bipolar","fase depresiva bipolar"]},
    {"cie10":"F34.0","cie11":"6A62","nombre":"Ciclotimia","cap":"F · Mental","tags":["ciclotimia","humor cíclico","bipolar suave","oscilaciones humor"]},
    # Depresión
    {"cie10":"F32","cie11":"6A70","nombre":"Episodio depresivo","cap":"F · Mental","tags":["depresion","depresión","episodio depresivo","tristeza","anhedonia","PHQ9","TDM","trastorno depresivo"]},
    {"cie10":"F32.0","cie11":"6A70.0","nombre":"Episodio depresivo leve","cap":"F · Mental","tags":["depresion leve","depresión leve","PHQ9 leve","tristeza leve"]},
    {"cie10":"F32.1","cie11":"6A70.1","nombre":"Episodio depresivo moderado","cap":"F · Mental","tags":["depresion moderada","depresión moderada","PHQ9 moderado","anhedonia moderada"]},
    {"cie10":"F32.2","cie11":"6A70.2","nombre":"Episodio depresivo grave sin síntomas psicóticos","cap":"F · Mental","tags":["depresion severa","depresión severa","depresión grave","PHQ9 severo","ideación suicida"]},
    {"cie10":"F32.3","cie11":"6A70.3","nombre":"Episodio depresivo grave con síntomas psicóticos","cap":"F · Mental","tags":["depresion psicótica","depresión grave psicosis"]},
    {"cie10":"F33","cie11":"6A71","nombre":"Trastorno depresivo recurrente","cap":"F · Mental","tags":["depresion recurrente","depresión recurrente","TDM recurrente","trastorno depresivo mayor"]},
    {"cie10":"F33.0","cie11":"6A71.0","nombre":"Trastorno depresivo recurrente, episodio leve actual","cap":"F · Mental","tags":["depresion recurrente leve","depresión recurrente leve"]},
    {"cie10":"F33.1","cie11":"6A71.1","nombre":"Trastorno depresivo recurrente, episodio moderado actual","cap":"F · Mental","tags":["depresion recurrente moderada","depresión recurrente moderada"]},
    {"cie10":"F33.2","cie11":"6A71.2","nombre":"Trastorno depresivo recurrente, episodio grave sin psicosis","cap":"F · Mental","tags":["depresion recurrente grave","depresión recurrente grave"]},
    {"cie10":"F34.1","cie11":"6A72","nombre":"Distimia (Trastorno depresivo persistente)","cap":"F · Mental","tags":["distimia","depresion crónica","depresión crónica","trastorno depresivo persistente","tristeza crónica"]},
    {"cie10":"F53","cie11":"6E40","nombre":"Trastorno depresivo del puerperio (depresión postparto)","cap":"F · Mental","tags":["postparto","depresion postparto","depresión postparto","puerperio","baby blues","tristeza postparto","psicosis puerperal"]},
    # Ansiedad
    {"cie10":"F40","cie11":"6B00","nombre":"Trastornos fóbicos de ansiedad","cap":"F · Mental","tags":["fobia","trastorno fóbico","miedo patológico","ansiedad fóbica"]},
    {"cie10":"F40.0","cie11":"6B01","nombre":"Agorafobia","cap":"F · Mental","tags":["agorafobia","miedo espacios abiertos","evitación lugares"]},
    {"cie10":"F40.1","cie11":"6B04","nombre":"Trastorno de ansiedad social [fobia social]","cap":"F · Mental","tags":["fobia social","ansiedad social","timidez patológica","vergüenza social"]},
    {"cie10":"F40.2","cie11":"6B03","nombre":"Fobias específicas","cap":"F · Mental","tags":["fobia específica","claustrofobia","fobia altura","fobia sangre","fobia animales"]},
    {"cie10":"F41","cie11":"6B00","nombre":"Otros trastornos de ansiedad","cap":"F · Mental","tags":["ansiedad","trastorno ansiedad","ansiedad general"]},
    {"cie10":"F41.0","cie11":"6B01","nombre":"Trastorno de pánico [ansiedad paroxística episódica]","cap":"F · Mental","tags":["panico","pánico","ataques de pánico","crisis de pánico","taquicardia pánico","angustia"]},
    {"cie10":"F41.1","cie11":"6B00","nombre":"Trastorno de ansiedad generalizada (TAG)","cap":"F · Mental","tags":["GAD","GAD7","TAG","ansiedad generalizada","preocupación excesiva","ansiedad crónica"]},
    {"cie10":"F41.2","cie11":"6B0Z","nombre":"Trastorno mixto ansioso-depresivo","cap":"F · Mental","tags":["ansiedad depresion mixta","ansiedad depresión mixta","trastorno mixto","comorbilidad"]},
    {"cie10":"F42","cie11":"6B20","nombre":"Trastorno obsesivo-compulsivo (TOC)","cap":"F · Mental","tags":["TOC","OCD","obsesivo compulsivo","obsesiones","compulsiones","rituales"]},
    # Estrés y trauma
    {"cie10":"F43","cie11":"6B40","nombre":"Reacción al estrés grave y trastornos de adaptación","cap":"F · Mental","tags":["estrés","trauma","adaptación","PTSD","TEPT"]},
    {"cie10":"F43.0","cie11":"6B40","nombre":"Reacción aguda al estrés","cap":"F · Mental","tags":["estrés agudo","reacción aguda","trauma agudo","shock emocional"]},
    {"cie10":"F43.1","cie11":"6B40","nombre":"Trastorno de estrés postraumático (PTSD / TEPT)","cap":"F · Mental","tags":["PTSD","TEPT","estrés postraumático","trauma","flashback","pesadillas","abuso"]},
    {"cie10":"F43.2","cie11":"6B43","nombre":"Trastornos de adaptación","cap":"F · Mental","tags":["adaptacion","trastorno adaptativo","estrés situacional","duelo","adaptación"]},
    {"cie10":"F44","cie11":"6B60","nombre":"Trastornos disociativos [de conversión]","cap":"F · Mental","tags":["disociación","conversión","parálisis funcional","histeria","amnesia disociativa"]},
    # Somáticos
    {"cie10":"F45","cie11":"6C20","nombre":"Trastornos somatomorfos","cap":"F · Mental","tags":["somatomorfo","somatización","síntomas sin causa orgánica","hipocondría"]},
    {"cie10":"F45.2","cie11":"6C21","nombre":"Trastorno hipocondriaco","cap":"F · Mental","tags":["hipocondria","hipocondría","ansiedad enfermedad","miedo enfermar","salud ansiedad"]},
    {"cie10":"F45.4","cie11":"MG30","nombre":"Trastorno de dolor persistente somatomorfo","cap":"F · Mental","tags":["dolor crónico psicológico","dolor somatomorfo","dolor funcional","dolor sin causa orgánica"]},
    # Sueño
    {"cie10":"F51","cie11":"7A00","nombre":"Trastornos no orgánicos del sueño","cap":"F · Mental","tags":["insomnio","sueño","trastorno sueño","hipersomnia","pesadillas"]},
    {"cie10":"F51.0","cie11":"7A00","nombre":"Insomnio no orgánico","cap":"F · Mental","tags":["insomnio","dificultad dormir","insomnio crónico","sueño"]},
    # Alimentación
    {"cie10":"F50","cie11":"6B80","nombre":"Trastornos de la ingestión de alimentos","cap":"F · Mental","tags":["TCA","anorexia","bulimia","conducta alimentaria"]},
    {"cie10":"F50.0","cie11":"6B80.0","nombre":"Anorexia nerviosa","cap":"F · Mental","tags":["anorexia","anorexia nerviosa","restricción alimentaria","imagen corporal","TCA"]},
    {"cie10":"F50.2","cie11":"6B81","nombre":"Bulimia nerviosa","cap":"F · Mental","tags":["bulimia","atracones","purgas","vómitos autoinducidos","TCA"]},
    # Personalidad
    {"cie10":"F60","cie11":"6D10","nombre":"Trastornos específicos de la personalidad","cap":"F · Mental","tags":["personalidad","trastorno personalidad","carácter patológico"]},
    {"cie10":"F60.0","cie11":"6D10.0","nombre":"Trastorno paranoide de la personalidad","cap":"F · Mental","tags":["personalidad paranoide","desconfianza","suspicacia"]},
    {"cie10":"F60.3","cie11":"6D11.5","nombre":"Trastorno emocionalmente inestable de la personalidad — Borderline (TLP)","cap":"F · Mental","tags":["borderline","TLP","límite personalidad","inestabilidad emocional","BPD"]},
    {"cie10":"F60.4","cie11":"6D10.4","nombre":"Trastorno histriónico de la personalidad","cap":"F · Mental","tags":["histriónico","dramatismo","teatralidad","seducción patológica"]},
    {"cie10":"F60.5","cie11":"6D10.5","nombre":"Trastorno anancástico [obsesivo-compulsivo] de la personalidad","cap":"F · Mental","tags":["anancástico","TOCP","obsesivo personalidad","perfeccionismo","rigidez"]},
    {"cie10":"F60.6","cie11":"6D10.6","nombre":"Trastorno ansioso [con evitación] de la personalidad","cap":"F · Mental","tags":["ansioso evitativo","personalidad ansiosa","inhibición social"]},
    {"cie10":"F60.7","cie11":"6D10.7","nombre":"Trastorno dependiente de la personalidad","cap":"F · Mental","tags":["personalidad dependiente","dependencia emocional","sumisión"]},
    # Neurodesarrollo
    {"cie10":"F84","cie11":"6A02","nombre":"Trastornos generalizados del desarrollo","cap":"F · Mental","tags":["autismo","TEA","espectro autista","Asperger","TGD"]},
    {"cie10":"F84.0","cie11":"6A02","nombre":"Autismo infantil — Trastorno del Espectro Autista (TEA)","cap":"F · Mental","tags":["autismo","TEA","espectro autista","neurodivergente"]},
    {"cie10":"F90","cie11":"6A05","nombre":"Trastornos hipercinéticos — TDAH","cap":"F · Mental","tags":["TDAH","TDA","ADHD","hiperactividad","déficit atención","impulsividad","concentración"]},
    {"cie10":"F90.0","cie11":"6A05.0","nombre":"TDAH — Perturbación de la actividad y la atención (predominantemente inatento)","cap":"F · Mental","tags":["TDA inatento","déficit atención","concentración","distracción"]},
    {"cie10":"F90.1","cie11":"6A05.1","nombre":"TDAH — Trastorno hipercinético de la conducta (hiperactivo-impulsivo)","cap":"F · Mental","tags":["TDAH hiperactivo","impulsividad","hiperactividad motora"]},
    # Discapacidad intelectual
    {"cie10":"F70","cie11":"6A00","nombre":"Retraso mental leve — Discapacidad intelectual leve","cap":"F · Mental","tags":["discapacidad intelectual leve","retraso mental leve","CI 50-69"]},
    {"cie10":"F71","cie11":"6A01","nombre":"Retraso mental moderado — Discapacidad intelectual moderada","cap":"F · Mental","tags":["discapacidad intelectual moderada","CI 35-49"]},

    # ─────────────────────────────────────────────────────
    # CAP G · ENFERMEDADES DEL SISTEMA NERVIOSO
    # ─────────────────────────────────────────────────────
    {"cie10":"G20","cie11":"8A00","nombre":"Enfermedad de Parkinson","cap":"G · Nervioso","tags":["parkinson","temblor","rigidez","bradicinesia","dopamina","enfermedad Parkinson"]},
    {"cie10":"G25","cie11":"8A04","nombre":"Otros trastornos extrapiramidales y del movimiento","cap":"G · Nervioso","tags":["temblor esencial","distonía","tics","movimientos involuntarios"]},
    {"cie10":"G30","cie11":"8A20","nombre":"Enfermedad de Alzheimer","cap":"G · Nervioso","tags":["alzheimer","demencia","deterioro cognitivo","neurodegenerativo","memoria"]},
    {"cie10":"G35","cie11":"8A40","nombre":"Esclerosis múltiple","cap":"G · Nervioso","tags":["esclerosis múltiple","EM","desmielinizante","esclerosis"]},
    {"cie10":"G40","cie11":"8A60","nombre":"Epilepsia","cap":"G · Nervioso","tags":["epilepsia","convulsiones","crisis epiléptica","anticonvulsivo","carbamazepina","valproato"]},
    {"cie10":"G41","cie11":"8A61","nombre":"Estado de mal epiléptico","cap":"G · Nervioso","tags":["estado epiléptico","status epilepticus","convulsiones prolongadas"]},
    {"cie10":"G43","cie11":"8A80","nombre":"Migraña","cap":"G · Nervioso","tags":["migraña","jaqueca","cefalea migrañosa","aura","dolor de cabeza intenso"]},
    {"cie10":"G44","cie11":"8A81","nombre":"Otros síndromes de cefalea","cap":"G · Nervioso","tags":["cefalea","dolor de cabeza","cefalea tensional","cefalea crónica","cefalea cluster"]},
    {"cie10":"G45","cie11":"8B00","nombre":"Ataques de isquemia cerebral transitoria","cap":"G · Nervioso","tags":["AIT","isquemia cerebral transitoria","mini ACV","déficit neurológico transitorio"]},
    {"cie10":"G47","cie11":"7A00","nombre":"Trastornos del sueño","cap":"G · Nervioso","tags":["sueño","insomnio orgánico","apnea sueño","hipersomnia","narcolepsia","parasomnia"]},
    {"cie10":"G47.0","cie11":"7A00","nombre":"Trastornos del inicio y del mantenimiento del sueño [insomnio]","cap":"G · Nervioso","tags":["insomnio","dificultad dormir","sueño fragmentado","despertar nocturno"]},
    {"cie10":"G47.3","cie11":"7A41","nombre":"Apnea del sueño","cap":"G · Nervioso","tags":["apnea sueño","SAHOS","ronquido","oxigenación nocturna","CPAP","síndrome apnea"]},
    {"cie10":"G47.4","cie11":"7A80","nombre":"Narcolepsia y cataplejía","cap":"G · Nervioso","tags":["narcolepsia","somnolencia excesiva","cataplejía","hipersomnia"]},
    {"cie10":"G54","cie11":"8C10","nombre":"Trastornos de las raíces y de los plexos nerviosos","cap":"G · Nervioso","tags":["radiculopatía","hernia discal","ciática","neuropatía radicular","compresión nervio"]},
    {"cie10":"G62","cie11":"8C40","nombre":"Otras polineuropatías","cap":"G · Nervioso","tags":["neuropatía periférica","polineuropatía","hormigueo","adormecimiento","parestesia","neuropatía diabética"]},
    {"cie10":"G80","cie11":"8D20","nombre":"Parálisis cerebral infantil","cap":"G · Nervioso","tags":["parálisis cerebral","PC","PCI","daño neurológico motor"]},

    # ─────────────────────────────────────────────────────
    # CAP I · ENFERMEDADES DEL SISTEMA CIRCULATORIO
    # ─────────────────────────────────────────────────────
    {"cie10":"I10","cie11":"BA00","nombre":"Hipertensión esencial (primaria)","cap":"I · Circulatorio","tags":["hipertensión","HTA","presión alta","hipertensión arterial","antihipertensivo","tensión arterial"]},
    {"cie10":"I11","cie11":"BA01","nombre":"Enfermedad cardíaca hipertensiva","cap":"I · Circulatorio","tags":["cardiopatía hipertensiva","corazón hipertensión","HTA cardiaca"]},
    {"cie10":"I15","cie11":"BA03","nombre":"Hipertensión secundaria","cap":"I · Circulatorio","tags":["hipertensión secundaria","HTA secundaria","causa hipertensión"]},
    {"cie10":"I20","cie11":"BA80","nombre":"Angina de pecho","cap":"I · Circulatorio","tags":["angina","angina de pecho","dolor torácico isquémico","cardiopatía coronaria"]},
    {"cie10":"I21","cie11":"BA41","nombre":"Infarto agudo del miocardio","cap":"I · Circulatorio","tags":["infarto","IAM","infarto miocardio","ataque cardíaco","infarto agudo"]},
    {"cie10":"I25","cie11":"BA80","nombre":"Enfermedad isquémica crónica del corazón","cap":"I · Circulatorio","tags":["cardiopatía isquémica crónica","coronaria","arteria coronaria","corazón"]},
    {"cie10":"I42","cie11":"BC43","nombre":"Cardiomiopatía","cap":"I · Circulatorio","tags":["miocardiopatía","cardiomiopatía","corazón dilatado"]},
    {"cie10":"I47","cie11":"BC83","nombre":"Taquicardia paroxística","cap":"I · Circulatorio","tags":["taquicardia","taquicardia paroxística","SVT","taquiarritmia"]},
    {"cie10":"I48","cie11":"BC81","nombre":"Fibrilación y aleteo auricular","cap":"I · Circulatorio","tags":["fibrilación auricular","FA","arritmia","palpitaciones","anticoagulante"]},
    {"cie10":"I49","cie11":"BC84","nombre":"Otras arritmias cardíacas","cap":"I · Circulatorio","tags":["arritmia","extrasístoles","taquicardia","bradicardia","palpitaciones"]},
    {"cie10":"I50","cie11":"BD10","nombre":"Insuficiencia cardíaca","cap":"I · Circulatorio","tags":["insuficiencia cardiaca","falla cardiaca","edema cardiaco","disnea cardíaca","ICC"]},
    {"cie10":"I60","cie11":"8B00","nombre":"Hemorragia subaracnoidea","cap":"I · Circulatorio","tags":["hemorragia subaracnoidea","HSA","aneurisma roto","hemorragia cerebral"]},
    {"cie10":"I61","cie11":"8B01","nombre":"Hemorragia intraencefálica","cap":"I · Circulatorio","tags":["hemorragia cerebral","ACV hemorrágico","hematoma cerebral"]},
    {"cie10":"I63","cie11":"8B11","nombre":"Infarto cerebral","cap":"I · Circulatorio","tags":["infarto cerebral","ACV isquémico","ictus","accidente cerebrovascular","stroke"]},
    {"cie10":"I64","cie11":"8B2Z","nombre":"Accidente vascular encefálico agudo no especificado","cap":"I · Circulatorio","tags":["ACV","stroke","accidente cerebrovascular","parálisis facial","hemiplejía"]},
    {"cie10":"I70","cie11":"BA90","nombre":"Aterosclerosis","cap":"I · Circulatorio","tags":["aterosclerosis","placa arterial","arteriosclerosis","colesterol arterias"]},
    {"cie10":"I73","cie11":"BD50","nombre":"Otras enfermedades vasculares periféricas","cap":"I · Circulatorio","tags":["enfermedad arterial periférica","claudicación","isquemia piernas"]},
    {"cie10":"I83","cie11":"BD71","nombre":"Venas varicosas de extremidades inferiores","cap":"I · Circulatorio","tags":["várices","venas varicosas","insuficiencia venosa","varices piernas"]},
    {"cie10":"I95","cie11":"BA09","nombre":"Hipotensión","cap":"I · Circulatorio","tags":["hipotensión","presión baja","hipotensión arterial","mareo al pararse"]},

    # ─────────────────────────────────────────────────────
    # CAP J · ENFERMEDADES DEL SISTEMA RESPIRATORIO
    # ─────────────────────────────────────────────────────
    {"cie10":"J00","cie11":"CA00","nombre":"Rinofaringitis aguda [resfriado común]","cap":"J · Respiratorio","tags":["resfriado","resfrío","rinofaringitis","catarro","rinitis aguda","resfriado común"]},
    {"cie10":"J01","cie11":"CA01","nombre":"Sinusitis aguda","cap":"J · Respiratorio","tags":["sinusitis aguda","sinusitis","inflamación senos paranasales","dolor facial"]},
    {"cie10":"J02","cie11":"CA02","nombre":"Faringitis aguda","cap":"J · Respiratorio","tags":["faringitis","dolor de garganta","faringitis aguda","faringe inflamada"]},
    {"cie10":"J03","cie11":"CA03","nombre":"Amigdalitis aguda","cap":"J · Respiratorio","tags":["amigdalitis","angina","tonsilitis","dolor de garganta severo"]},
    {"cie10":"J06","cie11":"CA0Z","nombre":"Infecciones agudas de las vías respiratorias superiores","cap":"J · Respiratorio","tags":["IVAS","gripe","resfriado","infección respiratoria alta","infección vías altas"]},
    {"cie10":"J11","cie11":"1E32","nombre":"Influenza [gripe] debida a virus no identificado","cap":"J · Respiratorio","tags":["gripe","influenza","fiebre influenza","virus influenza","gripe estacional"]},
    {"cie10":"J12","cie11":"CA22","nombre":"Neumonía viral","cap":"J · Respiratorio","tags":["neumonía viral","neumonía virus","covid","SARS"]},
    {"cie10":"J18","cie11":"CA40","nombre":"Neumonía, organismo no especificado","cap":"J · Respiratorio","tags":["neumonía","pulmonía","infección pulmonar","consolidación pulmonar","neumonía bacteriana"]},
    {"cie10":"J20","cie11":"CA20","nombre":"Bronquitis aguda","cap":"J · Respiratorio","tags":["bronquitis aguda","infección bronquios","tos bronquitis","bronquitis"]},
    {"cie10":"J30","cie11":"CA07","nombre":"Rinitis alérgica y vasomotora","cap":"J · Respiratorio","tags":["rinitis alérgica","alergia nasal","rinitis","estornudos","congestión nasal"]},
    {"cie10":"J32","cie11":"CA01.Z","nombre":"Sinusitis crónica","cap":"J · Respiratorio","tags":["sinusitis crónica","sinusitis","senos paranasales crónicos"]},
    {"cie10":"J40","cie11":"CA21","nombre":"Bronquitis no especificada como aguda o crónica","cap":"J · Respiratorio","tags":["bronquitis","bronquitis crónica","tos crónica productiva"]},
    {"cie10":"J44","cie11":"CA22","nombre":"Otras enfermedades pulmonares obstructivas crónicas — EPOC","cap":"J · Respiratorio","tags":["EPOC","bronquitis crónica","enfisema","obstrucción respiratoria","FEV1","espirometría"]},
    {"cie10":"J45","cie11":"CA23","nombre":"Asma","cap":"J · Respiratorio","tags":["asma","broncoespasmo","sibilancias","asma bronquial","broncodilatador","salbutamol"]},
    {"cie10":"J45.0","cie11":"CA23.0","nombre":"Asma predominantemente alérgica","cap":"J · Respiratorio","tags":["asma alérgica","asma atópica","alergia respiratoria"]},

    # ─────────────────────────────────────────────────────
    # CAP K · ENFERMEDADES DEL SISTEMA DIGESTIVO
    # ─────────────────────────────────────────────────────
    {"cie10":"K02","cie11":"DA08","nombre":"Caries dental","cap":"K · Digestivo","tags":["caries","caries dental","odontología"]},
    {"cie10":"K20","cie11":"DA21","nombre":"Esofagitis","cap":"K · Digestivo","tags":["esofagitis","inflamación esófago","esofagitis erosiva"]},
    {"cie10":"K21","cie11":"DA22","nombre":"Enfermedad del reflujo gastroesofágico (ERGE)","cap":"K · Digestivo","tags":["reflujo","ERGE","pirosis","ardor estomacal","esofagitis por reflujo"]},
    {"cie10":"K25","cie11":"DA60","nombre":"Úlcera gástrica","cap":"K · Digestivo","tags":["úlcera gástrica","úlcera estómago","H. pylori","helicobacter","ulcera gastrica"]},
    {"cie10":"K26","cie11":"DA61","nombre":"Úlcera duodenal","cap":"K · Digestivo","tags":["úlcera duodenal","duodeno","H. pylori","dolor epigástrico","ulcera duodenal"]},
    {"cie10":"K29","cie11":"DA92","nombre":"Gastritis y duodenitis","cap":"K · Digestivo","tags":["gastritis","duodenitis","inflamación gástrica","epigastralgia","gastritis aguda"]},
    {"cie10":"K30","cie11":"DA93","nombre":"Dispepsia funcional","cap":"K · Digestivo","tags":["dispepsia","dispepsia funcional","malestar gástrico","epigastralgia funcional"]},
    {"cie10":"K35","cie11":"DC80","nombre":"Apendicitis aguda","cap":"K · Digestivo","tags":["apendicitis","apendicitis aguda","dolor fosa ilíaca derecha","fosa ilíaca"]},
    {"cie10":"K50","cie11":"DD70","nombre":"Enfermedad de Crohn [enteritis regional]","cap":"K · Digestivo","tags":["Crohn","enfermedad de Crohn","enteritis regional","EII"]},
    {"cie10":"K51","cie11":"DD71","nombre":"Colitis ulcerativa","cap":"K · Digestivo","tags":["colitis ulcerativa","colitis ulcerosa","CU","EII","colon inflamado"]},
    {"cie10":"K57","cie11":"DD90","nombre":"Enfermedad diverticular del intestino","cap":"K · Digestivo","tags":["diverticulitis","diverticulosis","divertículos colon"]},
    {"cie10":"K58","cie11":"DD90","nombre":"Síndrome del colon irritable (SII)","cap":"K · Digestivo","tags":["colon irritable","intestino irritable","SII","IBS","dispepsia funcional"]},
    {"cie10":"K64","cie11":"DC84","nombre":"Hemorroides y trombosis venosa perianal","cap":"K · Digestivo","tags":["hemorroides","almorranas","trombosis hemorroidal","proctología"]},
    {"cie10":"K70","cie11":"DB93","nombre":"Enfermedad alcohólica del hígado","cap":"K · Digestivo","tags":["hígado alcohólico","hepatitis alcohólica","cirrosis alcohólica","alcohol hígado"]},
    {"cie10":"K72","cie11":"DB92","nombre":"Insuficiencia hepática no clasificada en otra parte","cap":"K · Digestivo","tags":["insuficiencia hepática","falla hepática","hígado falla"]},
    {"cie10":"K73","cie11":"DB92","nombre":"Hepatitis crónica no clasificada en otra parte","cap":"K · Digestivo","tags":["hepatitis crónica","hepatitis B crónica","hepatitis C crónica"]},
    {"cie10":"K74","cie11":"DB98","nombre":"Fibrosis y cirrosis del hígado","cap":"K · Digestivo","tags":["cirrosis","fibrosis hepática","hepatopatía crónica","hígado cirrótico"]},
    {"cie10":"K80","cie11":"DC50","nombre":"Colelitiasis (cálculos biliares)","cap":"K · Digestivo","tags":["colelitiasis","cálculos biliares","litiasis biliar","vesícula","cólico biliar","piedras vesícula"]},
    {"cie10":"K81","cie11":"DC51","nombre":"Colecistitis","cap":"K · Digestivo","tags":["colecistitis","vesícula inflamada","cólico biliar","vesícula biliar"]},
    {"cie10":"K85","cie11":"DC31","nombre":"Pancreatitis aguda","cap":"K · Digestivo","tags":["pancreatitis aguda","páncreas inflamado","amilasa lipasa elevada"]},
    {"cie10":"K86","cie11":"DC32","nombre":"Otras enfermedades del páncreas","cap":"K · Digestivo","tags":["pancreatitis crónica","insuficiencia pancreática","páncreas"]},
    {"cie10":"K92","cie11":"DD93","nombre":"Otras enfermedades del sistema digestivo","cap":"K · Digestivo","tags":["hemorragia digestiva","melena","rectorragia","sangrado digestivo"]},

    # ─────────────────────────────────────────────────────
    # CAP L · ENFERMEDADES DE LA PIEL
    # ─────────────────────────────────────────────────────
    {"cie10":"L02","cie11":"1B72","nombre":"Absceso cutáneo, furúnculo y carbunco","cap":"L · Piel","tags":["absceso","furúnculo","carbunco","infección piel","celulitis focal"]},
    {"cie10":"L03","cie11":"1B72","nombre":"Celulitis","cap":"L · Piel","tags":["celulitis","infección tejido blando","celulitis infecciosa","erisipela"]},
    {"cie10":"L20","cie11":"EA80","nombre":"Dermatitis atópica","cap":"L · Piel","tags":["dermatitis atópica","eczema atópico","eccema","alergia piel","atopia"]},
    {"cie10":"L23","cie11":"EK00","nombre":"Dermatitis alérgica de contacto","cap":"L · Piel","tags":["dermatitis contacto alérgica","alergia contacto","eccema contacto"]},
    {"cie10":"L30","cie11":"EA88","nombre":"Otras dermatitis","cap":"L · Piel","tags":["dermatitis","eczema","picazón piel","prurito piel","dermatitis NOS"]},
    {"cie10":"L40","cie11":"EA90","nombre":"Psoriasis","cap":"L · Piel","tags":["psoriasis","piel escamosa","placas psoriasis","psoriasis vulgar"]},
    {"cie10":"L50","cie11":"EB01","nombre":"Urticaria","cap":"L · Piel","tags":["urticaria","ronchas","habones","alergia cutánea","antihistamínico"]},
    {"cie10":"L70","cie11":"ED80","nombre":"Acné","cap":"L · Piel","tags":["acné","acne","acné vulgar","comedones","espinillas"]},
    {"cie10":"L89","cie11":"EH90","nombre":"Úlcera de decúbito y por área de presión","cap":"L · Piel","tags":["úlcera decúbito","úlcera presión","escaras","llagas presión"]},

    # ─────────────────────────────────────────────────────
    # CAP M · ENFERMEDADES DEL SISTEMA OSTEOMUSCULAR
    # ─────────────────────────────────────────────────────
    {"cie10":"M05","cie11":"FA20","nombre":"Artritis reumatoide seropositiva","cap":"M · Osteomuscular","tags":["artritis reumatoide","AR seropositiva","factor reumatoide","anti-CCP"]},
    {"cie10":"M06","cie11":"FA20","nombre":"Otras artritis reumatoides","cap":"M · Osteomuscular","tags":["artritis reumatoide","AR","articulaciones","inflamación articular","autoinmune"]},
    {"cie10":"M08","cie11":"FA22","nombre":"Artritis juvenil","cap":"M · Osteomuscular","tags":["artritis juvenil","artritis niños","artritis reumatoide juvenil","AIJ"]},
    {"cie10":"M10","cie11":"FA90","nombre":"Gota","cap":"M · Osteomuscular","tags":["gota","hiperuricemia","ácido úrico","artritis gotosa","urato","podagra"]},
    {"cie10":"M15","cie11":"FA00","nombre":"Poliartrosis","cap":"M · Osteomuscular","tags":["artrosis","osteoartritis","degeneración articular","artrosis múltiple"]},
    {"cie10":"M16","cie11":"FA01","nombre":"Coxartrosis [artrosis de la cadera]","cap":"M · Osteomuscular","tags":["artrosis cadera","coxartrosis","dolor cadera","prótesis cadera"]},
    {"cie10":"M17","cie11":"FA02","nombre":"Gonartrosis [artrosis de la rodilla]","cap":"M · Osteomuscular","tags":["artrosis rodilla","gonartrosis","dolor rodilla","prótesis rodilla"]},
    {"cie10":"M32","cie11":"FA25","nombre":"Lupus eritematoso sistémico","cap":"M · Osteomuscular","tags":["lupus","LES","lupus sistémico","autoinmune","mariposa facial","ANA"]},
    {"cie10":"M45","cie11":"FA80","nombre":"Espondilitis anquilosante","cap":"M · Osteomuscular","tags":["espondilitis anquilosante","EA","sacroileítis","HLA-B27","columna vertebral"]},
    {"cie10":"M47","cie11":"FA84","nombre":"Espondilosis","cap":"M · Osteomuscular","tags":["espondilosis","artrosis vertebral","espondiloartrosis","columna vertebral","cervicalgia"]},
    {"cie10":"M50","cie11":"FA84","nombre":"Trastornos del disco cervical","cap":"M · Osteomuscular","tags":["hernia discal cervical","disco cervical","cervicalgia discal","protrusión cervical"]},
    {"cie10":"M51","cie11":"FA84","nombre":"Otros trastornos de los discos intervertebrales","cap":"M · Osteomuscular","tags":["hernia discal","disco intervertebral","hernia lumbar","ciática discal"]},
    {"cie10":"M54","cie11":"ME84","nombre":"Dorsalgia","cap":"M · Osteomuscular","tags":["dorsalgia","dolor espalda","lumbalgia","dolor lumbar","dolor dorsal"]},
    {"cie10":"M54.2","cie11":"ME84.2","nombre":"Cervicalgia","cap":"M · Osteomuscular","tags":["cervicalgia","dolor cervical","dolor cuello","contractura cervical","tortícolis"]},
    {"cie10":"M54.3","cie11":"ME84.3","nombre":"Ciática","cap":"M · Osteomuscular","tags":["ciática","ciatalgia","dolor irradiado pierna","nervio ciático","lumbociatalgia"]},
    {"cie10":"M54.5","cie11":"ME84.5","nombre":"Lumbago no especificado","cap":"M · Osteomuscular","tags":["lumbalgia","dolor lumbar","lumbago","dolor cintura","dolor bajo de espalda"]},
    {"cie10":"M75","cie11":"FB30","nombre":"Lesiones del hombro","cap":"M · Osteomuscular","tags":["hombro doloroso","manguito rotador","periartritis hombro","tendinitis hombro","bursitis hombro"]},
    {"cie10":"M79","cie11":"FB90","nombre":"Otros trastornos de los tejidos blandos","cap":"M · Osteomuscular","tags":["fibromialgia","mialgia","dolor muscular","tejidos blandos"]},
    {"cie10":"M79.7","cie11":"MG30.1","nombre":"Fibromialgia","cap":"M · Osteomuscular","tags":["fibromialgia","dolor difuso","fatiga crónica","sensibilidad dolor","síndrome fibromiálgico"]},
    {"cie10":"M80","cie11":"FB83","nombre":"Osteoporosis con fractura patológica","cap":"M · Osteomuscular","tags":["osteoporosis fractura","fractura patológica","densidad ósea baja"]},
    {"cie10":"M81","cie11":"FB83.1","nombre":"Osteoporosis sin fractura patológica","cap":"M · Osteomuscular","tags":["osteoporosis","densitometría","calcio hueso","bisfosfonatos"]},

    # ─────────────────────────────────────────────────────
    # CAP N · ENFERMEDADES DEL SISTEMA GENITOURINARIO
    # ─────────────────────────────────────────────────────
    {"cie10":"N17","cie11":"GB60","nombre":"Insuficiencia renal aguda","cap":"N · Genitourinario","tags":["insuficiencia renal aguda","IRA","falla renal aguda","creatinina elevada aguda"]},
    {"cie10":"N18","cie11":"GB61","nombre":"Enfermedad renal crónica (ERC)","cap":"N · Genitourinario","tags":["enfermedad renal crónica","ERC","insuficiencia renal crónica","diálisis","riñón"]},
    {"cie10":"N20","cie11":"GB80","nombre":"Cálculo del riñón y del uréter","cap":"N · Genitourinario","tags":["cálculos renales","litiasis renal","nefrolitiasis","piedras riñón","cólico renal"]},
    {"cie10":"N23","cie11":"GB81","nombre":"Cólico renal no especificado","cap":"N · Genitourinario","tags":["cólico renal","cólico nefrítico","dolor renal agudo"]},
    {"cie10":"N30","cie11":"GC20","nombre":"Cistitis","cap":"N · Genitourinario","tags":["cistitis","infección vejiga","ardor al orinar","disuria"]},
    {"cie10":"N39","cie11":"GC08","nombre":"Otros trastornos del sistema urinario","cap":"N · Genitourinario","tags":["infección urinaria","ITU","urocultivo","orina","bacteriuria"]},
    {"cie10":"N39.0","cie11":"GC08.0","nombre":"Infección del tracto urinario de sitio no especificado","cap":"N · Genitourinario","tags":["infección urinaria","ITU","cistitis","urocultivo","infección orina"]},
    {"cie10":"N40","cie11":"GC40","nombre":"Hiperplasia de la próstata","cap":"N · Genitourinario","tags":["hiperplasia prostática","HPB","próstata","micción","obstrucción urinaria","prostatismo"]},
    {"cie10":"N80","cie11":"GA10","nombre":"Endometriosis","cap":"N · Genitourinario","tags":["endometriosis","dolor pélvico crónico","dismenorrea","endometrio"]},
    {"cie10":"N91","cie11":"GA20","nombre":"Menstruación ausente, escasa o rara","cap":"N · Genitourinario","tags":["amenorrea","oligomenorrea","alteración menstrual","ciclo irregular"]},
    {"cie10":"N92","cie11":"GA21","nombre":"Menstruación excesiva, frecuente e irregular","cap":"N · Genitourinario","tags":["hipermenorrea","menorragia","sangrado excesivo","metrorragia"]},
    {"cie10":"N94","cie11":"GA20","nombre":"Dolor y otras afecciones relacionadas con los órganos genitales femeninos","cap":"N · Genitourinario","tags":["dispareunia","vulvodinia","dolor pélvico","dolor genital femenino"]},
    {"cie10":"N95","cie11":"GA30","nombre":"Otros trastornos menopáusicos y perimenopáusicos","cap":"N · Genitourinario","tags":["menopausia","climaterio","bochornos","sofocos","perimenopausia"]},
    {"cie10":"N97","cie11":"GA40","nombre":"Infertilidad femenina","cap":"N · Genitourinario","tags":["infertilidad femenina","esterilidad","fertilidad","ovulación"]},

    # ─────────────────────────────────────────────────────
    # CAP O · EMBARAZO, PARTO Y PUERPERIO
    # ─────────────────────────────────────────────────────
    {"cie10":"O03","cie11":"JA00","nombre":"Aborto espontáneo","cap":"O · Embarazo","tags":["aborto espontáneo","aborto","pérdida gestacional","miscarriage"]},
    {"cie10":"O10","cie11":"JA21","nombre":"Hipertensión preexistente que complica el embarazo","cap":"O · Embarazo","tags":["hipertensión embarazo","HTA gestacional crónica","HTA pregestacional"]},
    {"cie10":"O14","cie11":"JA23","nombre":"Preeclampsia","cap":"O · Embarazo","tags":["preeclampsia","hipertensión gestacional","proteína orina embarazo","toxemia"]},
    {"cie10":"O15","cie11":"JA24","nombre":"Eclampsia","cap":"O · Embarazo","tags":["eclampsia","convulsiones embarazo","urgencia obstétrica"]},
    {"cie10":"O24","cie11":"JA63","nombre":"Diabetes mellitus en el embarazo","cap":"O · Embarazo","tags":["diabetes gestacional","DMG","glucosa embarazo","diabetes embarazo"]},
    {"cie10":"O34","cie11":"JA82","nombre":"Atención materna por anormalidades de los órganos pelvianos","cap":"O · Embarazo","tags":["cesárea previa","útero cicatriz","presentación fetal","placenta previa"]},
    {"cie10":"O42","cie11":"JB06","nombre":"Ruptura prematura de las membranas","cap":"O · Embarazo","tags":["RPM","ruptura prematura membranas","rotura bolsa"]},
    {"cie10":"O60","cie11":"JB0D","nombre":"Trabajo de parto prematuro y parto","cap":"O · Embarazo","tags":["parto prematuro","trabajo parto prematuro","pretérmino"]},
    {"cie10":"O80","cie11":"JB40","nombre":"Parto único espontáneo","cap":"O · Embarazo","tags":["parto normal","parto vaginal","parto eutócico","parto espontáneo"]},
    {"cie10":"O82","cie11":"JB42","nombre":"Parto único por cesárea","cap":"O · Embarazo","tags":["cesárea","parto cesárea","cesárea programada","cesárea urgente"]},
    {"cie10":"O85","cie11":"JB40.1","nombre":"Sepsis puerperal","cap":"O · Embarazo","tags":["sepsis puerperal","infección puerperal","fiebre posparto"]},
    {"cie10":"O99","cie11":"JB6Z","nombre":"Otras enfermedades maternas clasificables en otra parte que complican el embarazo","cap":"O · Embarazo","tags":["complicación embarazo","enfermedad materna embarazo"]},

    # ─────────────────────────────────────────────────────
    # CAP R · SÍNTOMAS, SIGNOS Y HALLAZGOS ANORMALES
    # ─────────────────────────────────────────────────────
    {"cie10":"R00","cie11":"MC80","nombre":"Anormalidades del latido cardíaco (palpitaciones)","cap":"R · Síntomas","tags":["palpitaciones","taquicardia sintomática","bradicardia","latido irregular"]},
    {"cie10":"R05","cie11":"MD12","nombre":"Tos","cap":"R · Síntomas","tags":["tos","tos crónica","tos productiva","tos seca","tos persistente"]},
    {"cie10":"R06","cie11":"MD11","nombre":"Anormalidades de la respiración — disnea","cap":"R · Síntomas","tags":["disnea","dificultad respiratoria","falta de aire","ahogo","disnea de esfuerzo"]},
    {"cie10":"R10","cie11":"MD81","nombre":"Dolor abdominal y pélvico","cap":"R · Síntomas","tags":["dolor abdominal","epigastralgia","dolor pélvico","cólico abdominal","abdomen agudo"]},
    {"cie10":"R11","cie11":"MD90","nombre":"Náusea y vómito","cap":"R · Síntomas","tags":["náuseas","vómito","vómitos","náusea","emesis"]},
    {"cie10":"R42","cie11":"MB48","nombre":"Mareo y desvanecimiento","cap":"R · Síntomas","tags":["mareo","vértigo","desmayo","síncope","lipotimia","vahído"]},
    {"cie10":"R51","cie11":"MG31","nombre":"Cefalea","cap":"R · Síntomas","tags":["cefalea","dolor de cabeza","jaqueca","cefalalgia","cefalea inespecífica"]},
    {"cie10":"R52","cie11":"MG30","nombre":"Dolor no clasificado en otra parte","cap":"R · Síntomas","tags":["dolor inespecífico","dolor crónico","dolor NOS","dolor generalizado"]},
    {"cie10":"R53","cie11":"MG22","nombre":"Malestar y fatiga — astenia","cap":"R · Síntomas","tags":["fatiga","cansancio","astenia","malestar general","fatiga crónica","agotamiento"]},
    {"cie10":"R55","cie11":"MB44","nombre":"Síncope y colapso","cap":"R · Síntomas","tags":["síncope","desmayo","colapso","lipotimia","pérdida de consciencia"]},

    # ─────────────────────────────────────────────────────
    # CAP Z · FACTORES QUE INFLUYEN EN EL ESTADO DE SALUD
    # ─────────────────────────────────────────────────────
    {"cie10":"Z00","cie11":"QA00","nombre":"Examen general e investigación de personas sin quejas","cap":"Z · Factores salud","tags":["chequeo","control salud","examen general","preventivo","certificado médico","Z00"]},
    {"cie10":"Z03","cie11":"QA0B","nombre":"Observación y evaluación médicas por sospecha de enfermedades","cap":"Z · Factores salud","tags":["observación","evaluación","sospecha diagnóstica","descarte diagnóstico"]},
    {"cie10":"Z04","cie11":"QA0C","nombre":"Examen y observación por otras razones","cap":"Z · Factores salud","tags":["examen ocupacional","revisión médica","examen laboral","certificado"]},
    {"cie10":"Z09","cie11":"QA02","nombre":"Examen de seguimiento consecutivo a tratamiento por otras enfermedades","cap":"Z · Factores salud","tags":["seguimiento","control postratamiento","revisión control","alta médica","control"]},
    {"cie10":"Z11","cie11":"QA0H","nombre":"Examen de pesquisa especial para enfermedades infecciosas y parasitarias","cap":"Z · Factores salud","tags":["tamizaje infeccioso","screening infeccioso","VIH tamizaje","sífilis tamizaje"]},
    {"cie10":"Z12","cie11":"QA0H","nombre":"Examen de pesquisa especial para tumores","cap":"Z · Factores salud","tags":["tamizaje cáncer","screening oncológico","mamografía","papanicolau","colonoscopia"]},
    {"cie10":"Z13","cie11":"QA0H","nombre":"Examen de pesquisa especial para otras enfermedades y trastornos","cap":"Z · Factores salud","tags":["tamizaje","screening","detección precoz","cribado","despistaje"]},
    {"cie10":"Z23","cie11":"QA21","nombre":"Necesidad de inmunización contra enfermedad bacteriana única","cap":"Z · Factores salud","tags":["vacunación","inmunización","vacuna","profilaxis","vacunación adultos"]},
    {"cie10":"Z29","cie11":"QA21","nombre":"Necesidad de otras medidas profilácticas","cap":"Z · Factores salud","tags":["profilaxis","prevención","quimioprofilaxis","profilaxis post exposición"]},
    {"cie10":"Z30","cie11":"QA41","nombre":"Atención para la anticoncepción","cap":"Z · Factores salud","tags":["anticoncepción","anticonceptivos","planificación familiar","MAC"]},
    {"cie10":"Z34","cie11":"QA40","nombre":"Supervisión de embarazo normal — control prenatal","cap":"Z · Factores salud","tags":["embarazo normal","control prenatal","gestante","CPN","atención prenatal"]},
    {"cie10":"Z35","cie11":"QA41","nombre":"Supervisión de embarazo de alto riesgo","cap":"Z · Factores salud","tags":["embarazo alto riesgo","control prenatal alto riesgo","gestante riesgo"]},
    {"cie10":"Z39","cie11":"QA50","nombre":"Examen y atención del postparto","cap":"Z · Factores salud","tags":["control postparto","puerperio","atención postparto","visita postparto"]},
    {"cie10":"Z51","cie11":"QC4Z","nombre":"Otra atención médica","cap":"Z · Factores salud","tags":["quimioterapia","radioterapia","atención paliativa","tratamiento médico programado"]},
    {"cie10":"Z54","cie11":"QC60","nombre":"Convalecencia","cap":"Z · Factores salud","tags":["convalecencia","recuperación","postoperatorio","rehabilitación","reposo médico"]},
    {"cie10":"Z71","cie11":"QC5Y","nombre":"Personas en contacto con los servicios de salud para otras consultas y consejos","cap":"Z · Factores salud","tags":["consejo médico","asesoría médica","orientación salud","consulta preventiva","consejería"]},
    {"cie10":"Z72","cie11":"QC30","nombre":"Problemas relacionados con el estilo de vida","cap":"Z · Factores salud","tags":["estilo vida","tabaco","alcohol","sedentarismo","dieta","estilo de vida"]},
    {"cie10":"Z76","cie11":"QC6Z","nombre":"Personas en contacto con los servicios de salud en otras circunstancias","cap":"Z · Factores salud","tags":["receta repetida","medicación crónica","renovación receta","tratamiento crónico","Z76"]},
    {"cie10":"Z85","cie11":"QC82","nombre":"Historia personal de neoplasias malignas","cap":"Z · Factores salud","tags":["antecedente cáncer","historia oncológica","remisión cáncer","sobreviviente cáncer"]},
    {"cie10":"Z87","cie11":"QC82","nombre":"Historia personal de otras enfermedades y afecciones","cap":"Z · Factores salud","tags":["antecedentes personales","historia médica personal","antecedente patológico"]},
    {"cie10":"Z87.891","cie11":"QC45","nombre":"Uso a largo plazo de cannabinoides medicinales","cap":"Z · Factores salud","tags":["cannabis medicinal","CBD terapéutico","cannabinoide medicinal","THC medicinal","receta cannabis","tratamiento cannabis"]},
    {"cie10":"Z96","cie11":"QC4Y","nombre":"Presencia de implantes y prótesis funcionales","cap":"Z · Factores salud","tags":["prótesis","implante","marcapasos","válvula cardiaca","implante coclear","stent"]},

    # ── HÍGADO / METABOLISMO ──
    {"cie10":"K76.0","cie11":"DB94.0","nombre":"Síndrome de Gilbert (hiperbilirrubinemia benigna)","cap":"K · Digestivo","tags":["gilbert","síndrome de gilbert","hiperbilirrubinemia","bilirrubina elevada","ictericia benigna","UGT1A1","ictericia gilbert","gilbert hiperbilirrubinemia"]},
    {"cie10":"K76.1","cie11":"DB94","nombre":"Hígado graso no alcohólico (NASH/NAFLD)","cap":"K · Digestivo","tags":["hígado graso","nafld","nash","esteatosis hepática","esteatohepatitis","hígado graso no alcohólico"]},
    {"cie10":"K74.6","cie11":"DB93.1","nombre":"Cirrosis hepática","cap":"K · Digestivo","tags":["cirrosis","cirrosis hepática","fibrosis hepática","insuficiencia hepática","hipertensión portal"]},
    {"cie10":"K75.4","cie11":"DB95","nombre":"Hepatitis autoinmune","cap":"K · Digestivo","tags":["hepatitis autoinmune","hepatitis crónica activa","autoinmune hepático"]},
    {"cie10":"K83.0","cie11":"DC11","nombre":"Colangitis esclerosante primaria","cap":"K · Digestivo","tags":["colangitis","CEP","colangitis esclerosante","colangitis biliar primaria"]},

    # ── NEUROLÓGICO AMPLIADO ──
    {"cie10":"G10","cie11":"8A01.10","nombre":"Enfermedad de Huntington","cap":"G · Nervioso","tags":["huntington","corea de huntington","enfermedad huntington","corea hereditaria"]},
    {"cie10":"G12.2","cie11":"8B60","nombre":"Esclerosis Lateral Amiotrófica (ELA)","cap":"G · Nervioso","tags":["ELA","esclerosis lateral amiotrófica","Lou Gehrig","SLA","motoneurona","enfermedad motoneurona"]},
    {"cie10":"G25.0","cie11":"8A04","nombre":"Temblor esencial","cap":"G · Nervioso","tags":["temblor esencial","temblor benigno","tremor","temblor familiar","temblor acción"]},
    {"cie10":"G35","cie11":"8A40","nombre":"Esclerosis Múltiple","cap":"G · Nervioso","tags":["esclerosis múltiple","EM","SM","desmielinización","esclerosis placas","espasticidad EM"]},
    {"cie10":"G50.0","cie11":"8B82.0","nombre":"Neuralgia del trigémino","cap":"G · Nervioso","tags":["neuralgia trigémino","dolor facial","tic douloureux","neuralgia facial","trigémino"]},
    {"cie10":"G54","cie11":"8C10","nombre":"Radiculopatía / Ciática","cap":"G · Nervioso","tags":["radiculopatía","ciática","lumbociática","hernia disco","radiculalgia","sciatica","ciatalgia"]},
    {"cie10":"G62","cie11":"8C20","nombre":"Polineuropatía periférica","cap":"G · Nervioso","tags":["polineuropatía","neuropatía periférica","polineuritis","neuropatía diabética","neuropatía periférica"]},
    {"cie10":"G70","cie11":"8C60","nombre":"Miastenia gravis","cap":"G · Nervioso","tags":["miastenia gravis","miastenia","debilidad muscular autoinmune","anticuerpos receptor acetilcolina"]},
    {"cie10":"G80","cie11":"8D20","nombre":"Parálisis cerebral","cap":"G · Nervioso","tags":["parálisis cerebral","PC","spasticidad","diplegia","hemiplegia cerebral","encefalopatía"]},
    {"cie10":"G90","cie11":"8D80","nombre":"Disautonomía / Disfunción autonómica","cap":"G · Nervioso","tags":["disautonomía","disfunción autonómica","POTS","taquicardia ortostática","síncope vasovagal","POTS"]},
    {"cie10":"G93.3","cie11":"8E49","nombre":"Síndrome de fatiga crónica (SFC/ME)","cap":"G · Nervioso","tags":["fatiga crónica","SFC","encefalomielitis miálgica","ME/CFS","fatiga post-COVID","síndrome fatiga crónica"]},

    # ── DOLOR Y MUSCULOESQUELÉTICO AMPLIADO ──
    {"cie10":"M06.9","cie11":"FA20","nombre":"Artritis reumatoide","cap":"M · Osteomuscular","tags":["artritis reumatoide","AR","poliartritis","artritis inflamatoria","reumatoide","factor reumatoide"]},
    {"cie10":"M07","cie11":"FA30","nombre":"Artritis psoriásica","cap":"M · Osteomuscular","tags":["artritis psoriásica","psoriasis articular","artropatía psoriásica","SpA"]},
    {"cie10":"M10","cie11":"FA92","nombre":"Gota / Artritis gotosa","cap":"M · Osteomuscular","tags":["gota","hiperuricemia","artritis gotosa","ácido úrico elevado","podagra","tofos","hiperuricemia"]},
    {"cie10":"M16","cie11":"FA91.0","nombre":"Coxartrosis / Artrosis de cadera","cap":"M · Osteomuscular","tags":["coxartrosis","artrosis cadera","osteoartritis cadera","gonartrosis","desgaste cadera"]},
    {"cie10":"M17","cie11":"FA91.1","nombre":"Gonartrosis / Artrosis de rodilla","cap":"M · Osteomuscular","tags":["gonartrosis","artrosis rodilla","osteoartritis rodilla","desgaste rodilla","condromalacia"]},
    {"cie10":"M32","cie11":"FA22","nombre":"Lupus eritematoso sistémico (LES)","cap":"M · Osteomuscular","tags":["lupus","LES","lupus eritematoso","lupus sistémico","enfermedad autoinmune sistémica","LES"]},
    {"cie10":"M45","cie11":"FA91.2","nombre":"Espondilitis anquilosante","cap":"M · Osteomuscular","tags":["espondilitis anquilosante","EA","espondiloartritis","sacroileítis","HLA-B27","rigidez columna","espondilitis"]},
    {"cie10":"M51.1","cie11":"FA80","nombre":"Hernia discal lumbar","cap":"M · Osteomuscular","tags":["hernia discal","hernia disco lumbar","protrusión discal","hernia L4L5","hernia L5S1","prolapso disco"]},
    {"cie10":"M65","cie11":"FB52","nombre":"Tendinitis / Tenosinovitis","cap":"M · Osteomuscular","tags":["tendinitis","tenosinovitis","inflamación tendón","tendinopatía","manguito rotador","tendón aquiles"]},
    {"cie10":"M72.2","cie11":"FB52.1","nombre":"Fascitis plantar","cap":"M · Osteomuscular","tags":["fascitis plantar","talón","espolón calcáneo","dolor talón","plantar fasciitis","espolón"]},
    {"cie10":"M81","cie11":"FB83","nombre":"Osteoporosis","cap":"M · Osteomuscular","tags":["osteoporosis","osteopenia","baja densidad ósea","dexa","menopausia ósea","fractura osteoporótica"]},

    # ── ONCOLOGÍA ──
    {"cie10":"C16","cie11":"2B72","nombre":"Cáncer gástrico","cap":"C · Oncología","tags":["cáncer gástrico","cáncer estómago","tumor gástrico","adenocarcinoma gástrico"]},
    {"cie10":"C18","cie11":"2B90","nombre":"Cáncer colorrectal","cap":"C · Oncología","tags":["cáncer colon","cáncer recto","colorrectal","tumor colorrectal","CCR"]},
    {"cie10":"C34","cie11":"2C25","nombre":"Cáncer de pulmón","cap":"C · Oncología","tags":["cáncer pulmón","tumor pulmón","carcinoma broncogénico","CPCP","CPCNP","adenocarcinoma pulmón"]},
    {"cie10":"C50","cie11":"2C60","nombre":"Cáncer de mama","cap":"C · Oncología","tags":["cáncer mama","tumor mama","carcinoma mama","cáncer seno","neoplasia mama","mastectomía"]},
    {"cie10":"C53","cie11":"2C77","nombre":"Cáncer de cuello uterino","cap":"C · Oncología","tags":["cáncer cérvix","cáncer cuello uterino","carcinoma cervical","HPV cáncer","cervicouterino"]},
    {"cie10":"C61","cie11":"2C82","nombre":"Cáncer de próstata","cap":"C · Oncología","tags":["cáncer próstata","tumor próstata","carcinoma prostático","adenocarcinoma próstata","PSA elevado"]},
    {"cie10":"C70","cie11":"2A00","nombre":"Tumor del sistema nervioso central","cap":"C · Oncología","tags":["tumor cerebral","glioblastoma","meningioma","astrocitoma","glioma","tumor SNC","neoplasia SNC"]},
    {"cie10":"C81","cie11":"2A20","nombre":"Linfoma de Hodgkin","cap":"C · Oncología","tags":["linfoma hodgkin","linfoma","enfermedad Hodgkin"]},
    {"cie10":"C82","cie11":"2A60","nombre":"Linfoma no Hodgkin","cap":"C · Oncología","tags":["linfoma no hodgkin","LNH","linfoma difuso","linfoma folicular","linfoma células B"]},
    {"cie10":"C90","cie11":"2A83","nombre":"Mieloma múltiple","cap":"C · Oncología","tags":["mieloma múltiple","mieloma","plasmocitoma","gammpatía monoclonal"]},
    {"cie10":"C91","cie11":"2B30","nombre":"Leucemia linfocítica","cap":"C · Oncología","tags":["leucemia linfocítica","LLC","LLA","leucemia linfoblástica","leucemia crónica"]},
    {"cie10":"Z51.0","cie11":"QC80","nombre":"En tratamiento quimioterapia / cuidados paliativos","cap":"Z · Factores salud","tags":["quimioterapia","quimio","tratamiento oncológico","náuseas quimio","cuidados paliativos","paliativo","dolor oncológico"]},

    # ── PSIQUIATRÍA AMPLIADO ──
    {"cie10":"F20","cie11":"6A20","nombre":"Esquizofrenia","cap":"F · Mental","tags":["esquizofrenia","psicosis crónica","alucinaciones","delirios","síntomas positivos negativos"]},
    {"cie10":"F25","cie11":"6A24","nombre":"Trastorno esquizoafectivo","cap":"F · Mental","tags":["esquizoafectivo","psicosis afectiva","trastorno esquizoafectivo"]},
    {"cie10":"F31","cie11":"6A60","nombre":"Trastorno bipolar","cap":"F · Mental","tags":["bipolar","trastorno bipolar","manía","hipomanía","ciclos maníaco-depresivos","TAB","bipolaridad"]},
    {"cie10":"F60.3","cie11":"6D11","nombre":"Trastorno límite de la personalidad (TLP)","cap":"F · Mental","tags":["TLP","borderline","límite personalidad","trastorno límite","impulsividad","inestabilidad emocional"]},
    {"cie10":"F84.0","cie11":"6A02","nombre":"Trastorno del espectro autista (TEA)","cap":"F · Mental","tags":["autismo","TEA","trastorno espectro autista","asperger","ASD","autismo infantil"]},
    {"cie10":"F90","cie11":"6A05","nombre":"TDAH / Trastorno por déficit de atención e hiperactividad","cap":"F · Mental","tags":["tdah","TDAH","ADD","déficit atención","hiperactividad","trastorno atención","ADHD"]},
    {"cie10":"F95","cie11":"8A05","nombre":"Síndrome de Tourette / Tics","cap":"F · Mental","tags":["tourette","tics","síndrome tourette","tics motores","coprolalia","tics vocales"]},
    {"cie10":"F50","cie11":"6B80","nombre":"Anorexia nerviosa","cap":"F · Mental","tags":["anorexia","anorexia nerviosa","trastorno alimentario","TCA","restricción alimentaria"]},
    {"cie10":"F50.2","cie11":"6B81","nombre":"Bulimia nerviosa","cap":"F · Mental","tags":["bulimia","bulimia nerviosa","TCA","atracones","purgas","trastorno alimentario"]},

    # ── ENDOCRINO AMPLIADO ──
    {"cie10":"E28.2","cie11":"5A90","nombre":"Síndrome de ovario poliquístico (SOP)","cap":"E · Endócrino","tags":["SOP","ovario poliquístico","PCOS","hiperandrogenismo","anovulación","resistencia insulina SOP","SOP infertilidad"]},
    {"cie10":"E66","cie11":"5B81","nombre":"Obesidad","cap":"E · Endócrino","tags":["obesidad","sobrepeso","IMC elevado","adiposidad","obesidad mórbida","obesidad grado 3"]},
    {"cie10":"E78","cie11":"5C80","nombre":"Dislipidemia / Hipercolesterolemia","cap":"E · Endócrino","tags":["dislipidemia","colesterol alto","hipercolesterolemia","hipertrigliceridemia","LDL alto","lípidos alterados"]},
    {"cie10":"E83.1","cie11":"5C65","nombre":"Hemocromatosis","cap":"E · Endócrino","tags":["hemocromatosis","hierro elevado","ferritina alta","sobrecarga hierro","hemocromatosis hereditaria"]},
    {"cie10":"E24","cie11":"5A61","nombre":"Síndrome de Cushing","cap":"E · Endócrino","tags":["cushing","síndrome cushing","hipercortisolismo","cortisol elevado","cara luna"]},
    {"cie10":"E27.1","cie11":"5A70","nombre":"Insuficiencia suprarrenal / Addison","cap":"E · Endócrino","tags":["addison","insuficiencia suprarrenal","cortisol bajo","hiperpigmentación addison"]},

    # ── CARDIOVASCULAR AMPLIADO ──
    {"cie10":"I48","cie11":"BC81","nombre":"Fibrilación auricular","cap":"I · Cardiovascular","tags":["fibrilación auricular","FA","arritmia","flutter auricular","anticoagulación FA"]},
    {"cie10":"I50","cie11":"BD10","nombre":"Insuficiencia cardíaca congestiva","cap":"I · Cardiovascular","tags":["insuficiencia cardíaca","ICC","falla cardíaca","cardiopatía descompensada","IC sistólica","IC diastólica"]},
    {"cie10":"I63","cie11":"8B11","nombre":"Accidente cerebrovascular isquémico (ACV)","cap":"I · Cardiovascular","tags":["ACV","stroke","accidente cerebrovascular","ictus","infarto cerebral","trombosis cerebral","hemiplegia ACV"]},
    {"cie10":"I87","cie11":"BD54","nombre":"Trombosis venosa profunda (TVP)","cap":"I · Cardiovascular","tags":["TVP","trombosis venosa profunda","trombo","tromboflebitis","TEP","embolia pulmonar"]},

    # ── RESPIRATORIO AMPLIADO ──
    {"cie10":"J44","cie11":"CA22","nombre":"EPOC / Enfermedad pulmonar obstructiva crónica","cap":"J · Respiratorio","tags":["EPOC","enfermedad pulmonar obstructiva","bronquitis crónica","enfisema","disnea EPOC"]},
    {"cie10":"J84","cie11":"CB03","nombre":"Fibrosis pulmonar / Enfermedad pulmonar intersticial","cap":"J · Respiratorio","tags":["fibrosis pulmonar","EPI","intersticial","FPI","fibrosis pulmonar idiopática"]},

    # ── RENAL / UROLÓGICO ──
    {"cie10":"N18","cie11":"GB61","nombre":"Enfermedad renal crónica (ERC)","cap":"N · Genitourinario","tags":["ERC","insuficiencia renal crónica","creatinina elevada","filtrado glomerular bajo","IRC","renal crónico"]},
    {"cie10":"N80","cie11":"GA10","nombre":"Endometriosis","cap":"N · Genitourinario","tags":["endometriosis","dolor pélvico","dismenorrea","infertilidad endometriosis","adenomiosis","endometriosis"]},
    {"cie10":"N95","cie11":"GA30","nombre":"Menopausia / Síntomas climatéricos","cap":"N · Genitourinario","tags":["menopausia","climaterio","sofocos","bochornos","síntomas climatéricos","climaterio"]},

    # ── DERMATOLOGÍA ──
    {"cie10":"L20","cie11":"EA80","nombre":"Dermatitis atópica / Eccema","cap":"L · Piel","tags":["dermatitis atópica","eccema","atopia","piel seca","eczema","dermatitis infantil"]},
    {"cie10":"L40","cie11":"EA90","nombre":"Psoriasis","cap":"L · Piel","tags":["psoriasis","placas psoriásicas","psoriasis vulgar","psoriasis en placas"]},
    {"cie10":"L90","cie11":"EF20","nombre":"Esclerodermia / Esclerosis sistémica","cap":"L · Piel","tags":["esclerodermia","esclerosis sistémica","morfea","piel endurecida","fibrosis dérmica"]},
]


def _norm(t: str) -> str:
    """Normaliza texto eliminando tildes para búsqueda tolerante."""
    return t.lower().translate(str.maketrans(
        "áéíóúàèìòùäëïöüñÁÉÍÓÚÑ",
        "aeiouaeiouaeiounaeioun"
    ))


def buscar_diagnostico(query: str, limite: int = 12) -> list:
    """
    Busca diagnósticos por código CIE-10, CIE-11 o nombre/tags.
    Tolerante a tildes y mayúsculas.
    """
    if not query or len(query.strip()) < 2:
        return []

    q  = query.lower().strip()
    qn = _norm(q)
    res = []

    for d in DIAGNOSTICOS:
        score = 0
        c10 = d["cie10"].lower()
        c11 = d["cie11"].lower()
        nom = _norm(d["nombre"])
        tags_n = [_norm(t) for t in d["tags"]]

        # Código exacto
        if q in (c10, c11):
            score = 100
        # Código empieza con la búsqueda
        elif c10.startswith(q) or c11.startswith(q):
            score = 88
        # Primer tag exacto (alias prioritario)
        elif tags_n and tags_n[0] == qn:
            score = 82
        # Nombre empieza con la búsqueda
        elif nom.startswith(qn):
            score = 75
        # Tag exacto
        elif qn in tags_n:
            score = 70
        # Nombre contiene la búsqueda — penalizar nombres largos
        elif qn in nom:
            score = 60 - min(len(d["nombre"]) // 12, 8)
        # Tag empieza con la búsqueda
        elif any(t.startswith(qn) for t in tags_n):
            score = 50
        # Tag contiene la búsqueda
        elif any(qn in t for t in tags_n):
            score = 40

        if score > 0:
            res.append({**d, "_score": score})

    res.sort(key=lambda x: (-x["_score"], len(x["cie10"]), x["cie10"]))
    return res[:limite]


def formato_opcion(d: dict) -> str:
    return f"{d['cie10']} / {d['cie11']} — {d['nombre']}"


def capitulos_disponibles() -> list:
    caps = sorted(set(d["cap"] for d in DIAGNOSTICOS))
    return ["Todos"] + caps
