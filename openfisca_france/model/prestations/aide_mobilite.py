from numpy import fabs, timedelta64
from openfisca_core.populations import ADD

from openfisca_france.model.base import Individu, Variable, MONTH, Enum, not_, \
    set_input_dispatch_by_period, set_input_divide_by_period, min_, select, date
from openfisca_france.model.caracteristiques_socio_demographiques.logement import TypesLieuResidence


class aide_mobilite_date_demande(Variable):
    value_type = date
    default_value = date(2021, 6, 9)
    entity = Individu
    label = "Date de demande d'évaluation à l'éligibilité de l'aide à la mobilité (AMOB) - (date du fait générateur)"
    definition_period = MONTH
    set_input = set_input_dispatch_by_period
    reference = "http://www.bo-pole-emploi.org/bulletinsofficiels/deliberation-n-2021-42-du-8-juin-2021-bope-n2021-43.html?type=dossiers/2021/bope-n-2021-043-du-11-juin-2021"


class TypesCategoriesDemandeurEmploi(Enum):
    __order__ = 'pas_de_categorie categorie_1 categorie_2 categorie_3 categorie_4 categorie_5 categorie_6 categorie_7 categorie_8' \
                # Needed to preserve the enum order in Python 2
    pas_de_categorie = "Aucune catégorie"
    categorie_1 = "Catégorie 1 - Personnes sans emploi, immédiatement disponibles en recherche de CDI plein temps."
    categorie_2 = "Catégorie 2 - Personnes sans emploi, immédiatement disponibles en recherche de CDI à temps partiel."
    categorie_3 = "Catégorie 3 - Personnes sans emploi, immédiatement disponibles en recherche de CDD."
    categorie_4 = "Catégorie 4 - Personnes sans emploi, non immédiatement disponibles et à la recherche d’un emploi."
    categorie_5 = "Catégorie 5 - Personnes non immédiatement disponibles, parce que titulaires d'un ou de plusieurs emplois, et à la recherche d'un autre emploi."
    categorie_6 = "Catégorie 6 - Personnes non immédiatement disponibles, en recherche d'un autre emploi en CDI à plein temps."
    categorie_7 = "Catégorie 7 - Personnes non immédiatement disponibles, en recherche d'un autre emploi en CDI à temps partiel."
    categorie_8 = "Catégorie 8 - Personnes non immédiatement disponibles, en recherche d'un autre emploi en CDD."


class pole_emploi_categorie_demandeur_emploi(Variable):
    reference = [
        "http://www.bo-pole-emploi.org/bulletinsofficiels/instruction-n2016-33-du-6-octobr.html?type=dossiers/2016/bope-n2016-80-du-17-novembre-201#",
        "Annexe 3 : la fiche 3 - Les effets de l’inscription"
        ]
    value_type = Enum
    possible_values = TypesCategoriesDemandeurEmploi
    default_value = TypesCategoriesDemandeurEmploi.pas_de_categorie
    entity = Individu
    label = "Le classement des demandeurs d’emploi dans les différentes catégories d’inscription à Pôle Emploi"
    definition_period = MONTH


class TypesContrat(Enum):
    __order__ = 'aucun cdi cdd ctt formation'  # Needed to preserve the enum order in Python 2
    aucun = "Aucun contrat"
    cdi = "Contrat à durée indéterminé (CDI)"
    cdd = "Contrat à durée déterminé (CDD)"
    ctt = "Contrat de travail temporaire (CTT)"
    formation = "Formation"


class types_contrat(Variable):
    value_type = Enum
    possible_values = TypesContrat
    default_value = TypesContrat.aucun
    entity = Individu
    label = "Types de contrat"
    definition_period = MONTH


class duree_formation(Variable):
    value_type = float
    entity = Individu
    label = "Durée de la formation en heures"
    definition_period = MONTH
    set_input = set_input_divide_by_period


class en_contrat_aide(Variable):
    value_type = bool
    entity = Individu
    label = "L'individu est en contrat aidé"
    definition_period = MONTH
    set_input = set_input_dispatch_by_period


class TypesLieuEmploiFormation(Enum):
    non_renseigne = "Non renseigné"
    metropole = "Métropole"
    france_hors_dom_corse = "France hors DOM et hors Corse"
    guadeloupe = "Guadeloupe"
    martinique = "Martinique"
    guyane = "Guyane"
    la_reunion = "La réunion"
    saint_pierre_et_miquelon = "Saint Pierre et Miquelon"
    mayotte = "Mayotte"
    saint_bartelemy = "Saint Bartelemy"
    saint_martin = "Saint Martin"


class lieu_emploi_ou_formation(Variable):
    value_type = Enum
    possible_values = TypesLieuEmploiFormation
    default_value = TypesLieuEmploiFormation.non_renseigne
    entity = Individu
    label = "Zone de l'emploi ou de la formation"
    definition_period = MONTH
    set_input = set_input_dispatch_by_period

    def formula_2021_06_09(individu, period):
        return select(
            [
                individu('lieu_emploi_formation_metropole', period),
                individu('lieu_emploi_formation_france_hors_dom_corse', period),
                individu('lieu_emploi_formation_guadeloupe', period),
                individu('lieu_emploi_formation_martinique', period),
                individu('lieu_emploi_formation_guyane', period),
                individu('lieu_emploi_formation_reunion', period),
                individu('lieu_emploi_formation_saint_pierre_et_miquelon', period),
                individu('lieu_emploi_formation_mayotte', period),
                individu('lieu_emploi_formation_saint_bartelemy', period),
                individu('lieu_emploi_formation_saint_martin', period)
                ],
            [
                TypesLieuEmploiFormation.metropole,
                TypesLieuEmploiFormation.france_hors_dom_corse,
                TypesLieuEmploiFormation.guadeloupe,
                TypesLieuEmploiFormation.martinique,
                TypesLieuEmploiFormation.guyane,
                TypesLieuEmploiFormation.la_reunion,
                TypesLieuEmploiFormation.saint_pierre_et_miquelon,
                TypesLieuEmploiFormation.mayotte,
                TypesLieuEmploiFormation.saint_bartelemy,
                TypesLieuEmploiFormation.saint_martin
                ],
            default=TypesLieuEmploiFormation.non_renseigne
            )


class distance_aller_retour_activite_domicile(Variable):
    entity = Individu
    value_type = float
    reference = "http://www.bo-pole-emploi.org/bulletinsofficiels/deliberation-n-2021-42-du-8-juin-2021-bope-n2021-43.html?type=dossiers/2021/bope-n-2021-043-du-11-juin-2021"
    label = "Distance en kilomètres entre le lieu de l’entretien d’embauche, la reprise d’emploi, la formation, la prestation d’accompagnement, " \
            "l’immersion professionnelle (PMSMP), le concours public ou l’examen certifiant et le lieu de résidence du demandeur d'emploi"
    definition_period = MONTH
    set_input = set_input_dispatch_by_period


class nombre_allers_retours(Variable):
    entity = Individu
    value_type = float
    reference = "http://www.bo-pole-emploi.org/bulletinsofficiels/deliberation-n-2021-42-du-8-juin-2021-bope-n2021-43.html?type=dossiers/2021/bope-n-2021-043-du-11-juin-2021"
    label = "Nombre d'aller/retour pour le calcul de l'aide à la mobilité de Pôle emploi - AMOB"
    definition_period = MONTH
    set_input = set_input_dispatch_by_period


class aide_mobilite_duree_trajet(Variable):
    entity = Individu
    value_type = float
    reference = "http://www.bo-pole-emploi.org/bulletinsofficiels/deliberation-n-2021-42-du-8-juin-2021-bope-n2021-43.html?type=dossiers/2021/bope-n-2021-043-du-11-juin-2021"
    label = "Durée en minutes entre le lieu de l’entretien d’embauche, la reprise d’emploi, la formation, la prestation d’accompagnement, " \
            "l’immersion professionnelle (PMSMP), le concours public ou l’examen certifiant et le lieu de résidence du demandeur d'emploi"
    definition_period = MONTH
    set_input = set_input_dispatch_by_period


class nuitees(Variable):
    entity = Individu
    value_type = int
    reference = [
        "http://www.bo-pole-emploi.org/bulletinsofficiels/deliberation-n-2021-42-du-8-juin-2021-bope-n2021-43.html?type=dossiers/2021/bope-n-2021-043-du-11-juin-2021"
        ]
    label = "Nombre de nuitées pour le calcul de l'aide à la mobilité de Pôle emploi - AMOB"
    definition_period = MONTH
    set_input = set_input_dispatch_by_period


class repas(Variable):
    entity = Individu
    value_type = int
    reference = [
        "http://www.bo-pole-emploi.org/bulletinsofficiels/deliberation-n-2021-42-du-8-juin-2021-bope-n2021-43.html?type=dossiers/2021/bope-n-2021-043-du-11-juin-2021"
        ]
    label = "Nombre de repas pour le calcul de l'aide à la mobilité de Pôle emploi - AMOB"
    definition_period = MONTH
    set_input = set_input_dispatch_by_period


class ContexteActivitePoleEmploi(Enum):
    __order__ = 'indetermine formation reprise_emploi recherche_emploi'  # Needed to preserve the enum order in Python 2
    indetermine = "Indeterminé"
    formation = "En formation"
    reprise_emploi = "En reprise d'emploi"
    recherche_emploi = "En recherche d'emploi"


class contexte_activite_pole_emploi(Variable):
    value_type = Enum
    possible_values = ContexteActivitePoleEmploi
    default_value = ContexteActivitePoleEmploi.indetermine
    entity = Individu
    label = "Les différents contextes d'activité pour le calcul de l'aide à la mobilité de Pôle Emploi - AMOB "
    definition_period = MONTH


class DispositifsDeFormation(Enum):
    __order__ = 'autre bilan_competences permis_conduire_b accompagnement_creation_entreprise accompagnement_validation_acquis'  # Needed to preserve the enum order in Python 2
    autre = "Autre formation"
    bilan_competences = "Bilan de compétences"
    permis_conduire_b = "Permis de conduire B (code et/ou conduite)"
    accompagnement_creation_entreprise = "Accompagnement à la création d'entreprise"
    accompagnement_validation_acquis = "Accompagnement à la validation des acquis de l'experience (VAE)"


class dispositifs_formation(Variable):
    value_type = Enum
    possible_values = DispositifsDeFormation
    default_value = DispositifsDeFormation.autre
    entity = Individu
    label = "Dispositifs de formation"
    definition_period = MONTH


class formation_validee_pole_emploi(Variable):
    value_type = bool
    entity = Individu
    label = "La formation de l'individu est validée par Pôle emploi"
    definition_period = MONTH
    set_input = set_input_dispatch_by_period


class formation_financee_ou_cofinancee(Variable):
    value_type = bool
    entity = Individu
    label = "La formation de l'individu est financée ou cofinancée (compte personnel de formation (CPF), fonds propres, Pôle Emploi, un tiers)"
    definition_period = MONTH
    set_input = set_input_dispatch_by_period


class TypesActiviteEnRechercheEmploi(Enum):
    __order__ = 'indeterminee entretien_embauche concours_public examen_certifiant prestation_accompagnement immersion_professionnelle_PMSMP'  # Needed to preserve the enum order in Python 2
    indeterminee = "Activité indéterminée"
    entretien_embauche = "Entretien d'embauche"
    concours_public = "Concours public"
    examen_certifiant = "Examen certifiant"
    prestation_accompagnement = "Prestation d'accompagnement"
    immersion_professionnelle_PMSMP = "Immersion professionnelle PMSMP"


class types_activite_en_recherche_emploi(Variable):
    value_type = Enum
    possible_values = TypesActiviteEnRechercheEmploi
    default_value = TypesActiviteEnRechercheEmploi.indeterminee
    entity = Individu
    label = "Les types d'activité dans un contexte de recherche d'emploi pour l'aide à la mobilité de Pôle Emploi - AMOB"
    definition_period = MONTH


class aide_mobilite_categories_demandeur_emploi_eligibles(Variable):
    value_type = bool
    entity = Individu
    label = "Le demandeur d'emploi appartient à une catégorie éligible pour l'aide à la mobilité - AMOB"
    definition_period = MONTH
    set_input = set_input_divide_by_period
    reference = "http://www.bo-pole-emploi.org/bulletinsofficiels/deliberation-n-2021-42-du-8-juin-2021-bope-n2021-43.html?type=dossiers/2021/bope-n-2021-043-du-11-juin-2021"

    def formula_2021_06_09(individu, period, parameters):

        pe_categorie_demandeur_emploi = individu('pole_emploi_categorie_demandeur_emploi', period)

        stagiaire_formation_professionnelle = individu('stagiaire', period)
        contrat_aide = individu('en_contrat_aide', period)

        categorie_4 = pe_categorie_demandeur_emploi == TypesCategoriesDemandeurEmploi.categorie_4
        categorie_4_stagiaire_formation_professionnelle = categorie_4 * stagiaire_formation_professionnelle

        categorie_5 = pe_categorie_demandeur_emploi == TypesCategoriesDemandeurEmploi.categorie_5
        categorie_5_contrat_aide = categorie_5 * contrat_aide

        categories_eligibles = ((pe_categorie_demandeur_emploi == TypesCategoriesDemandeurEmploi.categorie_1)
                                + (pe_categorie_demandeur_emploi == TypesCategoriesDemandeurEmploi.categorie_2)
                                + (pe_categorie_demandeur_emploi == TypesCategoriesDemandeurEmploi.categorie_3)
                                + (categorie_4_stagiaire_formation_professionnelle + categorie_5_contrat_aide)
                                + (pe_categorie_demandeur_emploi == TypesCategoriesDemandeurEmploi.categorie_6)
                                + (pe_categorie_demandeur_emploi == TypesCategoriesDemandeurEmploi.categorie_7)
                                + (pe_categorie_demandeur_emploi == TypesCategoriesDemandeurEmploi.categorie_8))

        return categories_eligibles


class aide_mobilite_allocations_eligibles(Variable):
    value_type = bool
    entity = Individu
    label = "Le demandeur d'emploi touche un montant d'allocation éligible pour l'aide à la mobilité - AMOB"
    definition_period = MONTH
    set_input = set_input_divide_by_period
    reference = "http://www.bo-pole-emploi.org/bulletinsofficiels/deliberation-n-2021-42-du-8-juin-2021-bope-n2021-43.html?type=dossiers/2021/bope-n-2021-043-du-11-juin-2021"

    def formula_2021_06_09(individu, period, parameters):
        epsilon = 0.0001
        lieu_de_residence = individu.menage('residence', period)
        mayotte = lieu_de_residence == TypesLieuResidence.mayotte
        hors_mayotte = not_(mayotte)

        allocation_individu = individu('allocation_retour_emploi', period)
        allocations = parameters(period).chomage.allocation_retour_emploi
        allocation_minimale_hors_mayotte = allocations.montant_minimum * hors_mayotte
        allocation_minimale_mayotte = allocations.montant_minimum_mayotte * mayotte

        allocation_minimale_en_fonction_de_la_region = allocation_minimale_hors_mayotte + allocation_minimale_mayotte

        are_individu_egale_are_min = fabs(allocation_individu - allocation_minimale_en_fonction_de_la_region) < epsilon
        are_individu_inferieure_are_min = allocation_individu < allocation_minimale_en_fonction_de_la_region

        return are_individu_inferieure_are_min + are_individu_egale_are_min


class aide_mobilite_eligible(Variable):
    value_type = bool
    entity = Individu
    label = "Eligibilité à l'aide à la mobilité de Pôle Emploi - AMOB"
    definition_period = MONTH
    set_input = set_input_divide_by_period
    reference = "http://www.bo-pole-emploi.org/bulletinsofficiels/deliberation-n-2021-42-du-8-juin-2021-bope-n2021-43.html?type=dossiers/2021/bope-n-2021-043-du-11-juin-2021"
    documentation = '''
        1- L'individu doit être dans un contexte de recherche d'emploi, reprise d'emploi ou d'entrée en formation
            1.1 - Pour une formation ou une reprise d'emploi, la demande doit être faite au plus tard dans le mois suivant
            1.2 - Pour une recherche d'emploi, la demande doit être faite avant l'entretien d'embauche ou au plus tard dans un délai de 7 jours
        2- Sa reprise d'emploi ou son entretien d'emploi, cela doit concerner un cdi, cdd ou ctt de plus de 3 mois ou une formation de plus de 40h validée et financée
        3- L'individu est inscrit en catégorie 1, 2, 3, 4 "stagiaire de la formation professionnelle" ou 5 "contrat aidé", 6, 7 ou 8
        4- L'individu est non indemnisé ou son allocation est inférieure ou égale à l'ARE minimale
        5- L'emploi ou la formation se situe en France
        6-
            6.1 - Son "activité" doit être à plus de 60 km aller-retour de son lieu de résidence
            6.2 - Ou 20 km lorsque l'individu réside en dehors de la métropole
            6.3 - Ou 2 heures de trajet aller-retour
        7 - Les dispositifs suivants ne donne pas lieu au versement de l'aide à la mobilité :
            - le bilan de compétences
            - le permis de conduire B (code et/ou conduite)
            - l’accompagnement à la création d’entreprise
            - l’accompagnement à la validation des acquis de l’expérience (VAE)
    '''

    def formula_2021_06_09(individu, period, parameters):

        #  1
        contexte = individu('contexte_activite_pole_emploi', period)
        contrat_travail_debut = individu('contrat_de_travail_debut', period)
        date_debut_type_activite_recherche_emploi = individu('date_debut_recherche_emploi', period)
        contrat_de_travail_debut_en_mois = contrat_travail_debut.astype('M8[M]')
        amob_date_de_demande = individu("aide_mobilite_date_demande", period)
        parametres_amob = parameters(period).prestations_sociales.aide_mobilite
        date_contrat_limite_contexte_formation_reprise = min_((contrat_de_travail_debut_en_mois + 1) + (contrat_travail_debut - contrat_de_travail_debut_en_mois),
                                               (contrat_de_travail_debut_en_mois + 2) - timedelta64(1, 'D'))
        dates_demandes_amob_eligibles_formation_reprise = amob_date_de_demande <= date_contrat_limite_contexte_formation_reprise

        date_limite_contrat_contexte_recherche = date_debut_type_activite_recherche_emploi + (parametres_amob.delai_max - 1)  # 7 jours de date à date
        dates_demandes_amob_eligibles_recherche = amob_date_de_demande <= date_limite_contrat_contexte_recherche

        en_recherche_emploi = contexte == ContexteActivitePoleEmploi.recherche_emploi
        en_reprise_emploi = contexte == ContexteActivitePoleEmploi.reprise_emploi
        en_formation = contexte == ContexteActivitePoleEmploi.formation

        contextes_eligibles = (en_recherche_emploi * dates_demandes_amob_eligibles_recherche) \
            + ((en_reprise_emploi + en_formation) * dates_demandes_amob_eligibles_formation_reprise)

        #  2
        activite_en_recherche_emploi = individu('types_activite_en_recherche_emploi', period)
        reprises_emploi_types_activites = individu('types_contrat', period)
        formation_validee = individu('formation_validee_pole_emploi', period)
        formation_financee = individu('formation_financee_ou_cofinancee', period)

        # Activites en recherche d'emploi
        en_entretien_embauche = (activite_en_recherche_emploi == TypesActiviteEnRechercheEmploi.entretien_embauche) * en_recherche_emploi

        activites_en_recherche_emploi_eligibles = not_((activite_en_recherche_emploi == TypesActiviteEnRechercheEmploi.entretien_embauche)
            + (activite_en_recherche_emploi == TypesActiviteEnRechercheEmploi.indeterminee)) \
            * en_recherche_emploi

        reprises_types_activites_formation = reprises_emploi_types_activites == TypesContrat.formation
        reprises_types_activites_cdi = reprises_emploi_types_activites == TypesContrat.cdi
        reprises_types_activites_cdd_ctt = (reprises_emploi_types_activites == TypesContrat.cdd) + (reprises_emploi_types_activites == TypesContrat.ctt)

        #  La formation doit être supérieure ou égale à 40 heures
        duree_formation = individu('duree_formation', period)
        periode_formation_eligible = duree_formation >= parametres_amob.duree_de_formation_minimum

        #  Le durée de contrat de l'emploi doit être d'au moins 3 mois
        duree_de_contrat_3_mois_minimum = individu('contrat_de_travail_duree', period) >= parametres_amob.duree_de_contrat_minimum

        reprises_cdd_ctt_eligibles = reprises_types_activites_cdd_ctt * duree_de_contrat_3_mois_minimum

        types_et_duree_activite_eligibles = (((reprises_types_activites_cdi + reprises_cdd_ctt_eligibles) * (en_reprise_emploi + en_entretien_embauche))
                                            + (reprises_types_activites_formation
                                               * en_formation
                                               * formation_validee
                                               * formation_financee
                                               * periode_formation_eligible))

        activites_eligibles = (types_et_duree_activite_eligibles + activites_en_recherche_emploi_eligibles)

        #  3
        categories_eligibles = individu('aide_mobilite_categories_demandeur_emploi_eligibles', period)

        #  4
        montants_allocations_eligibles = individu('aide_mobilite_allocations_eligibles', period)

        #  5
        lieux_activite_eligibles = not_(individu('lieu_emploi_ou_formation', period) == TypesLieuEmploiFormation.non_renseigne)

        #  6
        lieu_de_residence = individu.menage('residence', period)
        temps_de_trajet = individu('aide_mobilite_duree_trajet', period)
        distance_aller_retour = individu('distance_aller_retour_activite_domicile', period)

        temps_de_trajet_min = parametres_amob.duree_trajet_minimum
        reside_en_metropole = lieu_de_residence == TypesLieuResidence.metropole
        residence_renseignee = not_(lieu_de_residence == TypesLieuResidence.non_renseigne)

        distances_et_durees_aller_retour_eligibles = (((distance_aller_retour > parametres_amob.distance_minimum.metropole) * reside_en_metropole)
                                                    + ((distance_aller_retour > parametres_amob.distance_minimum.hors_metropole) * (not_(reside_en_metropole) * residence_renseignee))
                                                    + ((temps_de_trajet > temps_de_trajet_min) * residence_renseignee))

        #  7
        dispositifs_formations = individu('dispositifs_formation', period)
        dispositifs_formations_eligibles = dispositifs_formations == DispositifsDeFormation.autre

        eligibilite_amob = (contextes_eligibles
                       * activites_eligibles
                       * categories_eligibles
                       * montants_allocations_eligibles
                       * lieux_activite_eligibles
                       * distances_et_durees_aller_retour_eligibles
                       * dispositifs_formations_eligibles)

        return eligibilite_amob


class aide_mobilite(Variable):
    value_type = float
    entity = Individu
    label = "Calcul du montant de l'aide à la mobilité - AMOB"
    definition_period = MONTH
    set_input = set_input_divide_by_period
    reference = "http://www.bo-pole-emploi.org/bulletinsofficiels/deliberation-n-2021-42-du-8-juin-2021-bope-n2021-43.html?type=dossiers/2021/bope-n-2021-043-du-11-juin-2021"

    def formula_2021_06_09(individu, period, parameters):

        eligibilite_amob = individu('aide_mobilite_eligible', period)
        parametres_amob = parameters(period).prestations_sociales.aide_mobilite

        annee_glissante = period.start.period('year').offset(-1)

        aide_mobilite_12_derniers_mois = individu('aide_mobilite', annee_glissante, options=[ADD])

        montant_max = parametres_amob.montants.maximum
        montant_amob_deja_percu = min_(montant_max, fabs(aide_mobilite_12_derniers_mois))
        distance_aller_retour = individu('distance_aller_retour_activite_domicile', period)
        nb_aller_retour = individu('nombre_allers_retours', period)
        nb_nuitees = individu('nuitees', period)
        nb_repas = individu('repas', period)

        montant = parametres_amob.montants

        montants_frais_deplacement = montant.deplacement * distance_aller_retour * nb_aller_retour
        montants_frais_hebergement = montant.hebergement * nb_nuitees
        montants_frais_repas = montant.repas * nb_repas

        montants_theoriques = montants_frais_deplacement + montants_frais_hebergement + montants_frais_repas
        montants_max_attribuables = montant_max - montant_amob_deja_percu

        montants_reels = min_(montants_theoriques, montants_max_attribuables)

        return montants_reels * eligibilite_amob


class aide_mobilite_bon_de_transport(Variable):
    value_type = bool
    entity = Individu
    label = "Attribution d'un bon de transport dans un contexte précis - AMOB"
    definition_period = MONTH
    set_input = set_input_divide_by_period
    reference = "http://www.bo-pole-emploi.org/bulletinsofficiels/deliberation-n-2021-42-du-8-juin-2021-bope-n2021-43.html?type=dossiers/2021/bope-n-2021-043-du-11-juin-2021"

    def formula_2021_06_09(individu, period):

        contexte = individu('contexte_activite_pole_emploi', period)
        en_recherche_emploi = contexte == ContexteActivitePoleEmploi.recherche_emploi
        lieux_activite_eligibles = individu('lieu_emploi_ou_formation', period) == TypesLieuEmploiFormation.france_hors_dom_corse
        categories_non_eligibles = not_(individu('aide_mobilite_categories_demandeur_emploi_eligibles', period))
        allocation_non_eligible = not_(individu('aide_mobilite_allocations_eligibles', period))

        return (en_recherche_emploi
            * lieux_activite_eligibles
            * categories_non_eligibles
            * allocation_non_eligible)