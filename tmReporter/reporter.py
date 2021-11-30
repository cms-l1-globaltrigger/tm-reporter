import copy
import datetime
import re
import sys, os

from jinja2 import Environment, FileSystemLoader, StrictUndefined

import tmEventSetup

from .filters import vhdl_label, vhdl_expression, expr2html, vhdl2html
from . import __version__

__all__ = ['Reporter', ]

esMuonTypes = (
    tmEventSetup.SingleMuon,
    tmEventSetup.DoubleMuon,
    tmEventSetup.TripleMuon,
    tmEventSetup.QuadMuon,
)

esEgammaTypes = (
    tmEventSetup.SingleEgamma,
    tmEventSetup.DoubleEgamma,
    tmEventSetup.TripleEgamma,
    tmEventSetup.QuadEgamma,
    tmEventSetup.SingleEgammaOvRm,
    tmEventSetup.DoubleEgammaOvRm,
    tmEventSetup.TripleEgammaOvRm,
    tmEventSetup.QuadEgammaOvRm,
)

esJetTypes = (
    tmEventSetup.SingleJet,
    tmEventSetup.DoubleJet,
    tmEventSetup.TripleJet,
    tmEventSetup.QuadJet,
    tmEventSetup.SingleJetOvRm,
    tmEventSetup.DoubleJetOvRm,
    tmEventSetup.TripleJetOvRm,
    tmEventSetup.QuadJetOvRm,
)

esTauTypes = (
    tmEventSetup.SingleTau,
    tmEventSetup.DoubleTau,
    tmEventSetup.TripleTau,
    tmEventSetup.QuadTau,
    tmEventSetup.SingleTauOvRm,
    tmEventSetup.DoubleTauOvRm,
    tmEventSetup.TripleTauOvRm,
    tmEventSetup.QuadTauOvRm,
)

esEnergySumsTypes = (
    tmEventSetup.TotalEt,
    tmEventSetup.TotalHt,
    tmEventSetup.TotalEtEM,
    tmEventSetup.MissingEt,
    tmEventSetup.MissingHt,
    tmEventSetup.MissingEtHF,
#    tmEventSetup.MissingHtHF,
    tmEventSetup.AsymmetryEt,
    tmEventSetup.AsymmetryHt,
    tmEventSetup.AsymmetryEtHF,
    tmEventSetup.AsymmetryHtHF,
)

esMinBiasHfTypes = (
    tmEventSetup.MinBiasHFM0,
    tmEventSetup.MinBiasHFM1,
    tmEventSetup.MinBiasHFP0,
    tmEventSetup.MinBiasHFP1,
)

esTowerCountTypes = (
    tmEventSetup.TowerCount,
)

esSignalTypes = (
    tmEventSetup.Centrality0,
    tmEventSetup.Centrality1,
    tmEventSetup.Centrality2,
    tmEventSetup.Centrality3,
    tmEventSetup.Centrality4,
    tmEventSetup.Centrality5,
    tmEventSetup.Centrality6,
    tmEventSetup.Centrality7,
    tmEventSetup.MuonShower0,
    tmEventSetup.MuonShower1,
    tmEventSetup.MuonShowerOutOfTime0,
    tmEventSetup.MuonShowerOutOfTime1,
)

esCorrelationTypes = (
    tmEventSetup.MuonMuonCorrelation,
    tmEventSetup.MuonEsumCorrelation,
    tmEventSetup.CaloMuonCorrelation,
    tmEventSetup.CaloCaloCorrelation,
    tmEventSetup.CaloEsumCorrelation,
    tmEventSetup.CaloCaloCorrelationOvRm,
)

esMassTypes = (
    tmEventSetup.InvariantMass,
    tmEventSetup.InvariantMass3,
    tmEventSetup.InvariantMassUpt,
    tmEventSetup.InvariantMassDeltaR,
    tmEventSetup.TransverseMass,
    tmEventSetup.InvariantMassOvRm,
)

esMuonGroup = "Muon"
esEgammaGroup = "E/gamma"
esJetGroup = "Jet"
esTauGroup = "Tau"
esEnergySumsGroup = "Energy Sums"
esMinBiasHfGroup = "Min Bias HF"
esTowerCountGroup = "Tower Count"
esCrossGroup = "Cross"
esCorrelationGroup = "Correlation"
esMassGroup = "Mass"
esExternalGroup = "External"
esSignalGroup = "Signal"

esTriggerGroups = (
    esMuonGroup,
    esEgammaGroup,
    esJetGroup,
    esTauGroup,
    esEnergySumsGroup,
    esMinBiasHfGroup,
    esTowerCountGroup,
    esCrossGroup,
    esCorrelationGroup,
    esMassGroup,
    esExternalGroup,
    esSignalGroup,
)

esCutType = {
    tmEventSetup.Threshold: 'Threshold',
    tmEventSetup.Eta: 'Eta',
    tmEventSetup.Phi: 'Phi',
    tmEventSetup.Charge: 'Charge',
    tmEventSetup.Quality: 'Quality',
    tmEventSetup.Isolation: 'Isolation',
    tmEventSetup.Displaced: 'Displaced',
    tmEventSetup.ImpactParameter: 'ImpactParameter',
    tmEventSetup.UnconstrainedPt: 'UnconstrainedPt',
    tmEventSetup.DeltaEta: 'DeltaEta',
    tmEventSetup.DeltaPhi: 'DeltaPhi',
    tmEventSetup.DeltaR: 'DeltaR',
    tmEventSetup.Mass: 'Mass',
    tmEventSetup.MassUpt: 'MassUpt',
    tmEventSetup.MassDeltaR: 'MassDeltaR',
    tmEventSetup.TwoBodyPt: 'TwoBodyPt',
    tmEventSetup.Slice: 'Slice',
    tmEventSetup.OvRmDeltaEta: 'OvRmDeltaEta',
    tmEventSetup.OvRmDeltaPhi: 'OvRmDeltaPhi',
    tmEventSetup.OvRmDeltaR: 'OvRmDeltaR',
    tmEventSetup.ChargeCorrelation: 'ChargeCorrelation',
    tmEventSetup.Count: 'Count',
}

# -----------------------------------------------------------------------------
#  Helpers
# -----------------------------------------------------------------------------

def getenv(name):
    """Get environment variable. Raises a RuntimeError exception if variable not set."""
    value = os.getenv(name)
    if value is None:
        raise RuntimeError("`{name}' environment not set".format(**locals()))
    return value

# -----------------------------------------------------------------------------
#  Structs
# -----------------------------------------------------------------------------

class MenuStub:
    """Menu template helper class.
    name             full menu name
    uuid_menu        UUID of originating menu
    uuid_firmware    UUID of firmware build
    scale_set        used scale set label
    grammar_version  grammar version of menu
    datetime         optional menu creation timestamp
    comment          optional menu comment
    algorithms       list of algorithm template helpers
    """
    def __init__(self, es):
        self.name = es.getName()
        self.uuid_menu = es.getMenuUuid()
        self.uuid_firmware = es.getFirmwareUuid()
        self.scale_set = es.getScaleSetName()
        self.externals_set = es._externals_set # not retrievable from esTriggerMenu
        self.grammar_version = es.getVersion()
        self.n_modules = es.getNmodules()
        self.datetime = es.getDatetime()
        self.comment = es.getComment()
        self.algorithms = self._getAlgorithms(es)
        self.cuts = self._getCuts(self.algorithms)
        self.labels = self._getLabels(self.algorithms)

    def _getAlgorithms(self, es):
        """Returns list of algorithm stubs sorted by index."""
        algorithmMapPtr = es.getAlgorithmMapPtr()
        algorithms = [AlgorithmStub(es, algorithm) for algorithm in es.getAlgorithmMapPtr().values()]
        algorithms.sort(key=lambda algorithm: algorithm.index)
        return algorithms

    def _getCuts(self, algorithms):
        """Returns sorted list of cut stubs."""
        cuts = {}
        for algorithm in algorithms:
            for condition in algorithm.conditions:
                for cut in condition.cuts:
                    if cut.name not in cuts:
                        cuts[cut.name] = copy.deepcopy(cut)
                for object in condition.objects:
                    for cut in object.cuts:
                        if cut.name not in cuts:
                            cuts[cut.name] = copy.deepcopy(cut)
        return sorted(cuts.values(), key=lambda cut: (cut.cutType, cut.objectType))

    def _getLabels(self, algorithms):
        """Returns sorted list of seed labels."""
        labels = set()
        for algorithm in algorithms:
            labels.update(algorithm.labels)
        return sorted(labels)

class AlgorithmStub:
    """Algorithm template helper class.
    name            full algorithm name
    index           global algorithm index (int)
    moduleId        module ID (int)
    moduleIndex     local module algorithm index (int)
    expression      original grammar notation of expression
    vhdlExpression  VHDL notation of expression
    rpnVector       reversed polish notation of expression
    comment         n/a
    conditions      list of condition template helpers
    """
    def __init__(self, es, ptr):
        self.name = ptr.getName()
        self.index = ptr.getIndex()
        self.moduleId = ptr.getModuleId()
        self.moduleIndex = ptr.getModuleIndex()
        self.expression = ptr.getExpression()
        self.vhdlExpression = ptr.getExpressionInCondition()
        self.rpnVector = ptr.getRpnVector()
        self.comment = self._getComment(self.name, es) # not retrievable from esAlgorithm
        self.labels = self._getLabels(self.name, es) # not retrievable from esAlgorithm
        self.conditions = self._getConditions(es)

    def _getConditions(self, es):
        """Returns list of condition stubs assigned to algorithm, sorted by order of appereance."""
        conditionMapPtr = es.getConditionMapPtr()
        conditions = {}
        mapping = self._getMapping()
        for token in self.rpnVector:
            if token in conditionMapPtr:
                conditions[token] = ConditionStub(es, conditionMapPtr[token], token=mapping[token])
        conditions = conditions.values()
        return sorted(conditions, key=lambda condition: self.rpnVector.index(condition.name))

    def _getMapping(self):
        """Returns token mapping."""
        mapping = {}
        # split expression and vhdl expression and try to map the tokens, thats just completely manky
        vhdlTokens = re.sub(r'[\(\)]', ' ', self.vhdlExpression).split() # remove braces and split
        exprTokens = re.sub(r'[\(\)]', ' ', self.expression).split()
        assert len(vhdlTokens) == len(exprTokens)
        for i in range(len(vhdlTokens)):
            mapping[vhdlTokens[i]] = exprTokens[i]
        return mapping

    def _getComment(self, name, es):
        """Pick algorithm comment from raw algorithms."""
        algorithm = es._algorithms[name]
        if 'comment' in algorithm:
            return algorithm['comment']
        return ""

    def _getLabels(self, name, es):
        """Pick algorithm labels from raw algorithms."""
        algorithm = es._algorithms[name]
        if 'labels' in algorithm:
            return sorted(algorithm['labels'].split(','))
        return []

class ConditionStub:
    """Condition template helper class.
    name     auto generated condtion name
    type     condition type (enum)
    objects  list of object template helpers
    cuts     list of cut template helpers
    token    expression token for display purposes
    """
    def __init__(self, es, ptr, token=None):
        self.name = ptr.getName()
        self.type = ptr.getType()
        self.objects = [ObjectStub(es, obj) for obj in ptr.getObjects()]
        self.cuts = [CutStub(es, cut) for cut in ptr.getCuts()]
        self.token = token or "" # store the expression notation for display purposes

class ObjectStub:
    """Object template helper class.
    name           full object name
    type           object type (enum)
    comparisonOperator  comparision operator (enum)
    bxOffset       bunch crossing offset (int)
    threshold      object threshold in GeV (float)
    extSignalName  external signal name (only valid for EXT type objects)
    extChannelId   channel id of external signal (only valid for EXT type objects)
    cuts           list of cut template helpers
    """
    def __init__(self, es, ptr):
        self.name = ptr.getName()
        self.type = ptr.getType()
        self.comparisonOperator = ptr.getComparisonOperator()
        self.bxOffset = ptr.getBxOffset()
        self.threshold = ptr.getThreshold() # in GeV
        self.extSignalName = ptr.getExternalSignalName()
        self.extChannelId = ptr.getExternalChannelId()
        self.cuts = [CutStub(es, cut) for cut in ptr.getCuts()]

class CutStub:
    """Cut template helper class.
    name             full cut name
    objectType       object type, optional (enum)
    cutType          cut type (enum)
    minimumValue     minimum range value (float)
    maximumValue     maximum range value (float)
    minimumValueRaw  raw minimum range value from menu (float)
    maximumValueRaw  raw maximum range value from menu (float)
    minimumIndex     minimum range index (int)
    maximumIndex     maximum range index (int)
    precision        assigned decimal precision for values (int)
    data             payload data (for non range cuts)
    key              scale access key
    """
    def __init__(self, es, ptr):
        self.name = ptr.getName()
        self.objectType = ptr.getObjectType()
        self.cutType = ptr.getCutType()
        self.minimumValue = ptr.getMinimumValue()
        self.maximumValue = ptr.getMaximumValue()
        # HACK Extend cut with raw values
        if self.cutType in [tmEventSetup.Threshold]:
            self.minimumValueRaw = self.minimumValue
            self.maximumValueRaw = self.maximumValue
        elif self.cutType in [tmEventSetup.Count]:
            self.minimumValueRaw = self.minimumValue
            self.maximumValueRaw = self.minimumValue
        else:
            cut = es._cuts[self.name]
            self.minimumValueRaw = float(cut['minimum'])
            self.maximumValueRaw = float(cut['maximum'])
        self.minimumIndex = ptr.getMinimumIndex()
        self.maximumIndex = ptr.getMaximumIndex()
        self.precision = ptr.getPrecision()
        self.data = ptr.getData()
        self.key = ptr.getKey()


# -----------------------------------------------------------------------------
#  Template engines with custom resource loader environment.
# -----------------------------------------------------------------------------

class TemplateEngine(object):
    """Custom tempalte engine class."""

    def __init__(self, searchpath, encoding='utf-8'):
        # Create Jinja environment.
        loader = FileSystemLoader(searchpath, encoding)
        self.environment = Environment(loader=loader, undefined=StrictUndefined)
        # Add filters
        self.environment.filters['exprColorize'] = expr2html
        self.environment.filters['vhdlColorize'] = vhdl2html
        self.environment.filters['vhdlLabel'] = vhdl_label
        self.environment.filters['vhdlExpression'] = vhdl_expression
        def html_newlines(value): return value.replace('\n', '<br/>\n')
        self.environment.filters['htmlNewlines'] = html_newlines
        def hex(value, n=1): return format(value, '0{n}x'.format(n=n))
        self.environment.filters['hex'] = hex

    def render(self, template, data={}):
        template = self.environment.get_template(template)
        return template.render(data)

# -----------------------------------------------------------------------------
#  Reporter class
# -----------------------------------------------------------------------------

class Reporter(object):
    """Reporter class."""

    def __init__(self, searchpath, eventSetup):
        # Template search path
        self.searchpath = searchpath
        # Initialize empty menu content.
        self.eventSetup = eventSetup

    def getTriggerGroups(self, menu):
        """Returns ordered list of trigger group tuples."""
        triggerGroups = {}
        def add_algorithm(group, algorithm):
            """Adds algorithm to trigger group dictionary, creates new sets on demand."""
            if group not in triggerGroups:
                triggerGroups[group] = set()
            triggerGroups[group].add(algorithm)
        # Categorize algorithms
        for algorithm in menu.algorithms:
            if len(algorithm.conditions) > 1:
                add_algorithm(esCrossGroup, algorithm)
            else:
                condition = algorithm.conditions[0]
                if condition.type in esMuonTypes:
                    add_algorithm(esMuonGroup, algorithm)
                elif condition.type in esEgammaTypes:
                    add_algorithm(esEgammaGroup, algorithm)
                elif condition.type in esJetTypes:
                    add_algorithm(esJetGroup, algorithm)
                elif condition.type in esTauTypes:
                    add_algorithm(esTauGroup, algorithm)
                elif condition.type in esEnergySumsTypes:
                    add_algorithm(esEnergySumsGroup, algorithm)
                elif condition.type in esMinBiasHfTypes:
                    add_algorithm(esMinBiasHfGroup, algorithm)
                elif condition.type in esTowerCountTypes:
                    add_algorithm(esTowerCountGroup, algorithm)
                elif condition.type in esCorrelationTypes:
                    add_algorithm(esCorrelationGroup, algorithm)
                elif condition.type in esMassTypes:
                    add_algorithm(esMassGroup, algorithm)
                elif condition.type == tmEventSetup.Externals:
                    add_algorithm(esExternalGroup, algorithm)
                elif condition.type in esSignalTypes:
                    add_algorithm(esSignalGroup, algorithm)
                else:
                    raise KeyError("unknown condition type")
        # Sort algorithms
        for group in triggerGroups:
            triggerGroups[group] = sorted(triggerGroups[group], key=lambda algorithm: algorithm.conditions[0].type)
            triggerGroups[group].sort(key=lambda algorithm: algorithm.index) # sort algorithms of group by index
        # Sort groups
        sortedTriggerGroups = []
        sortedKeys = sorted(triggerGroups.keys(), key=lambda group: esTriggerGroups.index(group))
        for group in sortedKeys:
            sortedTriggerGroups.append((group, triggerGroups[group]))
        return sortedTriggerGroups

    def render_html(self):
        """Render HTML report."""
        menu = MenuStub(self.eventSetup)
        data = dict(
            menu=menu,
            es=tmEventSetup,
            reporter=dict(
                timestamp=datetime.datetime.now().strftime("%F %T"),
                version=__version__,
            ),
        )
        return TemplateEngine(self.searchpath).render('report.html', data)

    def render_twiki(self):
        """Render TWIKI report."""
        menu = MenuStub(self.eventSetup)
        menu.triggerGroups = self.getTriggerGroups(menu)
        data = dict(menu=menu)
        return TemplateEngine(self.searchpath).render('report.twiki', data)

    def write_html(self, filename):
        """Write HTML report to file, provided for convenience."""
        with open(filename, 'w') as handle:
            handle.write(self.render_html())

    def write_twiki(self, filename):
        """Write TWIKI report to file, provided for convenience."""
        with open(filename, 'w') as handle:
            handle.write(self.render_twiki())
