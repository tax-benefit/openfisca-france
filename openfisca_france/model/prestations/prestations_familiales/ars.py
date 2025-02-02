from openfisca_france.model.base import *
from openfisca_france.model.prestations.prestations_familiales.base_ressource import nb_enf


class ars(Variable):
    value_type = float
    entity = Famille
    label = "Allocation de rentrée scolaire"
    reference = "http://vosdroits.service-public.fr/particuliers/F1878.xhtml"
    definition_period = YEAR

    def formula(famille, period, parameters):
        '''
        Allocation de rentrée scolaire brute de CRDS
        '''
        janvier = period.first_month
        septembre = period.start.offset('first-of', 'year').offset(9, 'month').period('month')
        af_nbenf = famille('af_nbenf', septembre)
        base_ressources = famille('prestations_familiales_base_ressources', janvier)
        ars = parameters(septembre).prestations_sociales.prestations_familiales.education_presence_parentale.ars
        af = parameters(septembre).prestations_sociales.prestations_familiales.prestations_generales.af
        # TODO: convention sur la mensualisation
        # On tient compte du fait qu'en cas de léger dépassement du plafond, une allocation dégressive
        # (appelée allocation différentielle), calculée en fonction des revenus, peut être versée.

        bmaf = af.bmaf
        # On doit prendre l'âge en septembre
        enf_05 = nb_enf(famille, septembre, ars.age_entree_primaire - 1, ars.age_entree_primaire - 1)  # 5 ans et 6 ans avant le 31 décembre
        # enf_05 = 0
        # Un enfant scolarisé qui n'a pas encore atteint l'âge de 6 ans
        # avant le 1er février 2012 peut donner droit à l'ARS à condition qu'il
        # soit inscrit à l'école primaire. Il faudra alors présenter un
        # certificat de scolarité.
        enf_primaire = enf_05 + nb_enf(famille, septembre, ars.age_entree_primaire, ars.age_entree_college - 1)
        enf_college = nb_enf(famille, septembre, ars.age_entree_college, ars.age_entree_lycee - 1)
        enf_lycee = nb_enf(famille, septembre, ars.age_entree_lycee, ars.age_sortie_lycee)

        arsnbenf = enf_primaire + enf_college + enf_lycee

        # Plafond en fonction du nb d'enfants A CHARGE (Cf. article R543)
        ars_plaf_res = ars.plafond_ressources * (1 + af_nbenf * ars.majoration_par_enf_supp)

        arsbase = bmaf * (
            ars.taux_primaire * enf_primaire
            + ars.taux_college * enf_college
            + ars.taux_lycee * enf_lycee
            )

        # Forme de l'ARS  en fonction des enfants a*n - (rev-plaf)/n
        # ars_diff = (ars_plaf_res + arsbase - base_ressources) / arsnbenf
        ars_montant = (arsnbenf > 0) * max_(0, arsbase - max_(0, (base_ressources - ars_plaf_res) / max_(1, arsnbenf)))

        return ars_montant * (ars_montant >= ars.montant_seuil_non_versement)
