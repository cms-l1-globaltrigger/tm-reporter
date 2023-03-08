import copy
import datetime
import os
import re
import sys
from typing import Any, Dict, List, Optional

from jinja2 import Environment, FileSystemLoader, StrictUndefined

import tmEventSetup

from . import __version__
from .filters import vhdl_label, vhdl_expression, expr2html, vhdl2html

__all__ = ["Reporter"]

esMuonTypes: List[int] = [
    tmEventSetup.SingleMuon,
    tmEventSetup.DoubleMuon,
    tmEventSetup.TripleMuon,
    tmEventSetup.QuadMuon,
]

esEgammaTypes: List[int] = [
    tmEventSetup.SingleEgamma,
    tmEventSetup.DoubleEgamma,
    tmEventSetup.TripleEgamma,
    tmEventSetup.QuadEgamma,
    tmEventSetup.SingleEgammaOvRm,
    tmEventSetup.DoubleEgammaOvRm,
    tmEventSetup.TripleEgammaOvRm,
    tmEventSetup.QuadEgammaOvRm,
]

esJetTypes: List[int] = [
    tmEventSetup.SingleJet,
    tmEventSetup.DoubleJet,
    tmEventSetup.TripleJet,
    tmEventSetup.QuadJet,
    tmEventSetup.SingleJetOvRm,
    tmEventSetup.DoubleJetOvRm,
    tmEventSetup.TripleJetOvRm,
    tmEventSetup.QuadJetOvRm,
]

esTauTypes: List[int] = [
    tmEventSetup.SingleTau,
    tmEventSetup.DoubleTau,
    tmEventSetup.TripleTau,
    tmEventSetup.QuadTau,
    tmEventSetup.SingleTauOvRm,
    tmEventSetup.DoubleTauOvRm,
    tmEventSetup.TripleTauOvRm,
    tmEventSetup.QuadTauOvRm,
]

esEnergySumsTypes: List[int] = [
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
]

esMinBiasHfTypes: List[int] = [
    tmEventSetup.MinBiasHFM0,
    tmEventSetup.MinBiasHFM1,
    tmEventSetup.MinBiasHFP0,
    tmEventSetup.MinBiasHFP1,
]

esTowerCountTypes: List[int] = [
    tmEventSetup.TowerCount,
    tmEventSetup.ZDCPlus,
    tmEventSetup.ZDCMinus,
]

esSignalTypes: List[int] = [
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
    tmEventSetup.MuonShower2,
    tmEventSetup.MuonShowerOutOfTime0,
    tmEventSetup.MuonShowerOutOfTime1,
    tmEventSetup.AnomalyDetectionTrigger,
]

esCorrelationTypes: List[int] = [
    tmEventSetup.MuonMuonCorrelation,
    tmEventSetup.MuonEsumCorrelation,
    tmEventSetup.CaloMuonCorrelation,
    tmEventSetup.CaloCaloCorrelation,
    tmEventSetup.CaloEsumCorrelation,
    tmEventSetup.CaloCaloCorrelationOvRm,
]

esMassTypes: List[int] = [
    tmEventSetup.InvariantMass,
    tmEventSetup.InvariantMass3,
    tmEventSetup.InvariantMassUpt,
    tmEventSetup.InvariantMassDeltaR,
    tmEventSetup.TransverseMass,
    tmEventSetup.InvariantMassOvRm,
]

esMuonGroup: str = "Muon"
esEgammaGroup: str = "E/gamma"
esJetGroup: str = "Jet"
esTauGroup: str = "Tau"
esEnergySumsGroup: str = "Energy Sums"
esMinBiasHfGroup: str = "Min Bias HF"
esTowerCountGroup: str = "Tower Count"
esCrossGroup: str = "Cross"
esCorrelationGroup: str = "Correlation"
esMassGroup: str = "Mass"
esExternalGroup: str = "External"
esSignalGroup: str = "Signal"

esTriggerGroups: List[str] = [
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
]

esCutType: Dict[int, str] = {
    tmEventSetup.Threshold: "Threshold",
    tmEventSetup.Eta: "Eta",
    tmEventSetup.Phi: "Phi",
    tmEventSetup.Charge: "Charge",
    tmEventSetup.Quality: "Quality",
    tmEventSetup.Isolation: "Isolation",
    tmEventSetup.Displaced: "Displaced",
    tmEventSetup.ImpactParameter: "ImpactParameter",
    tmEventSetup.UnconstrainedPt: "UnconstrainedPt",
    tmEventSetup.DeltaEta: "DeltaEta",
    tmEventSetup.DeltaPhi: "DeltaPhi",
    tmEventSetup.DeltaR: "DeltaR",
    tmEventSetup.Mass: "Mass",
    tmEventSetup.MassUpt: "MassUpt",
    tmEventSetup.MassDeltaR: "MassDeltaR",
    tmEventSetup.TwoBodyPt: "TwoBodyPt",
    tmEventSetup.Slice: "Slice",
    tmEventSetup.Index: "Index",
    tmEventSetup.AnomalyScore: "AnomalyScore",
    tmEventSetup.OvRmDeltaEta: "OvRmDeltaEta",
    tmEventSetup.OvRmDeltaPhi: "OvRmDeltaPhi",
    tmEventSetup.OvRmDeltaR: "OvRmDeltaR",
    tmEventSetup.ChargeCorrelation: "ChargeCorrelation",
    tmEventSetup.Count: "Count",
}


def getenv(name: str) -> str:
    """Get environment variable. Raises a RuntimeError exception if variable not set."""
    value = os.getenv(name)
    if value is None:
        raise RuntimeError("`{name}' environment not set".format(**locals()))
    return value


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
    def __init__(self, es, ptr) -> None:
        self.name: str = ptr.getName()
        self.objectType: int = ptr.getObjectType()
        self.cutType: int = ptr.getCutType()
        self.minimumValue: float = ptr.getMinimumValue()
        self.maximumValue: float = ptr.getMaximumValue()
        self.minimumValueRaw: float = 0.0
        self.maximumValueRaw: float = 0.0
        # HACK Extend cut with raw values
        if self.cutType in [tmEventSetup.Threshold]:
            self.minimumValueRaw = self.minimumValue
            self.maximumValueRaw = self.maximumValue
        elif self.cutType in [tmEventSetup.Count]:
            self.minimumValueRaw = self.minimumValue
            self.maximumValueRaw = self.minimumValue
        else:
            cut = es._cuts[self.name]
            self.minimumValueRaw = float(cut["minimum"])
            self.maximumValueRaw = float(cut["maximum"])
        self.minimumIndex: int = ptr.getMinimumIndex()
        self.maximumIndex: int = ptr.getMaximumIndex()
        self.precision: int = ptr.getPrecision()
        self.data: str = ptr.getData()
        self.key: str = ptr.getKey()


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
    def __init__(self, es, ptr) -> None:
        self.name: str = ptr.getName()
        self.type: int = ptr.getType()
        self.comparisonOperator: str = ptr.getComparisonOperator()
        self.bxOffset: int = ptr.getBxOffset()
        self.threshold: float = ptr.getThreshold() # in GeV
        self.extSignalName: str = ptr.getExternalSignalName()
        self.extChannelId: int = ptr.getExternalChannelId()
        self.cuts: List[CutStub] = self._getCuts(es, ptr)

    def _getCuts(self, es, ptr) -> List[CutStub]:
        return [CutStub(es, cut) for cut in ptr.getCuts()]


class ConditionStub:
    """Condition template helper class.
    name     auto generated condtion name
    type     condition type (enum)
    objects  list of object template helpers
    cuts     list of cut template helpers
    token    expression token for display purposes
    """
    def __init__(self, es, ptr, token: Optional[str] = None) -> None:
        self.name: str = ptr.getName()
        self.type: int = ptr.getType()
        self.objects: List[ObjectStub] = self._getObjects(es, ptr)
        self.cuts: List[CutStub] = self._getCuts(es, ptr)
        self.token: str = token or "" # store the expression notation for display purposes

    def _getObjects(self, es, ptr) -> List[ObjectStub]:
        return [ObjectStub(es, obj) for obj in ptr.getObjects()]

    def _getCuts(self, es, ptr) -> List[CutStub]:
        return [CutStub(es, cut) for cut in ptr.getCuts()]


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
    def __init__(self, es, ptr) -> None:
        self.name: str = ptr.getName()
        self.index: int = ptr.getIndex()
        self.moduleId: int = ptr.getModuleId()
        self.moduleIndex: int = ptr.getModuleIndex()
        self.expression: str = ptr.getExpression()
        self.vhdlExpression: str = ptr.getExpressionInCondition()
        self.rpnVector: List[str] = ptr.getRpnVector()
        self.comment: str = self._getComment(self.name, es) # not retrievable from esAlgorithm
        self.labels: List[str] = self._getLabels(self.name, es) # not retrievable from esAlgorithm
        self.conditions: List[ConditionStub] = self._getConditions(es)

    def _getConditions(self, es) -> List[ConditionStub]:
        """Returns list of condition stubs assigned to algorithm, sorted by order of appereance."""
        conditionMapPtr = es.getConditionMapPtr()
        conditions: Dict[str, ConditionStub] = {}
        mapping = self._getMapping()
        for token in self.rpnVector:
            if token in conditionMapPtr:
                conditions[token] = ConditionStub(es, conditionMapPtr[token], token=mapping[token])
        return sorted(conditions.values(), key=lambda condition: self.rpnVector.index(condition.name))

    def _getMapping(self) -> Dict[str, str]:
        """Returns token mapping."""
        mapping: Dict[str, str] = {}
        # split expression and vhdl expression and try to map the tokens, thats just completely manky
        vhdlTokens = re.sub(r"[\(\)]", " ", self.vhdlExpression).split() # remove braces and split
        exprTokens = re.sub(r"[\(\)]", " ", self.expression).split()
        assert len(vhdlTokens) == len(exprTokens)
        for i in range(len(vhdlTokens)):
            mapping[vhdlTokens[i]] = exprTokens[i]
        return mapping

    def _getComment(self, name: str, es) -> str:
        """Pick algorithm comment from raw algorithms."""
        algorithm = es._algorithms[name]
        if "comment" in algorithm:
            return algorithm["comment"]
        return ""

    def _getLabels(self, name: str, es) -> List[str]:
        """Pick algorithm labels from raw algorithms."""
        algorithm = es._algorithms[name]
        if "labels" in algorithm:
            return sorted(algorithm["labels"].split(","))
        return []


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
    def __init__(self, es) -> None:
        self.name: str = es.getName()
        self.uuid_menu: str = es.getMenuUuid()
        self.uuid_firmware: str = es.getFirmwareUuid()
        self.scale_set: str = es.getScaleSetName()
        self.externals_set: str = es._externals_set # not retrievable from esTriggerMenu
        self.grammar_version: str = es.getVersion()
        self.n_modules: int = es.getNmodules()
        self.datetime: str = es.getDatetime()
        self.comment: str = es.getComment()
        self.algorithms: List[AlgorithmStub] = self._getAlgorithms(es)
        self.cuts: List[CutStub] = self._getCuts(self.algorithms)
        self.labels: List[str] = self._getLabels(self.algorithms)
        self.triggerGroups: List = []

    def _getAlgorithms(self, es) -> List[AlgorithmStub]:
        """Returns list of algorithm stubs sorted by index."""
        algorithmMapPtr = es.getAlgorithmMapPtr()
        algorithms: List[AlgorithmStub] = [AlgorithmStub(es, algorithm) for algorithm in es.getAlgorithmMapPtr().values()]
        algorithms.sort(key=lambda algorithm: algorithm.index)
        return algorithms

    def _getCuts(self, algorithms: List[AlgorithmStub]) -> List[CutStub]:
        """Returns sorted list of cut stubs."""
        cuts: Dict[str, CutStub] = {}
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

    def _getLabels(self, algorithms: List[AlgorithmStub]) -> List[str]:
        """Returns sorted list of seed labels."""
        labels = set()
        for algorithm in algorithms:
            labels.update(algorithm.labels)
        return sorted(labels)


class TemplateEngine:
    """Custom template engine with resource loader environment.."""

    def __init__(self, searchpath: str, encoding: Optional[str] = None) -> None:
        # Create Jinja environment.
        loader = FileSystemLoader(searchpath, encoding or "utf-8")
        self.environment: Environment = Environment(loader=loader, undefined=StrictUndefined)

        # Add filters
        self.environment.filters["exprColorize"] = expr2html
        self.environment.filters["vhdlColorize"] = vhdl2html
        self.environment.filters["vhdlLabel"] = vhdl_label
        self.environment.filters["vhdlExpression"] = vhdl_expression

        def html_newlines(value):
            return value.replace("\n", "<br/>\n")

        self.environment.filters["htmlNewlines"] = html_newlines

        def hex(value, n=1):
            return format(value, "0{n}x".format(n=n))

        self.environment.filters["hex"] = hex

    def render(self, template: str, data: Optional[Dict[str, Any]] = None) -> str:
        return self.environment.get_template(template).render(data or {})


class Reporter:
    """Reporter class."""

    def __init__(self, searchpath: str, eventSetup) -> None:
        # Template search path
        self.searchpath: str = searchpath
        # Initialize empty menu content.
        self.eventSetup = eventSetup

    def getTriggerGroups(self, menu: MenuStub) -> List:
        """Returns ordered list of trigger group tuples."""
        triggerGroups: Dict[str, List[AlgorithmStub]] = {}

        def add_algorithm(group: str, algorithm: AlgorithmStub) -> None:
            """Adds algorithm to trigger group dictionary, creates new sets on demand."""
            if group not in triggerGroups:
                triggerGroups[group] = []
            if algorithm not in triggerGroups[group]:
                triggerGroups[group].append(algorithm)

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
                    raise KeyError(f"unknown condition type: {condition.type}")

        def sort_algorithms():
            for group in triggerGroups.values():
                group.sort(key=lambda algorithm: algorithm.conditions[0].type)
                group.sort(key=lambda algorithm: algorithm.index) # sort algorithms of group by index

        sort_algorithms()

        def sorted_groups() -> List:
            sortedTriggerGroups: List = []
            sortedKeys: List[str] = sorted(triggerGroups.keys(), key=lambda key: esTriggerGroups.index(key))
            for group in sortedKeys:
                sortedTriggerGroups.append((group, triggerGroups[group]))
            return sortedTriggerGroups

        return sorted_groups()

    def render_html(self) -> str:
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
        return TemplateEngine(self.searchpath).render("report.html", data)

    def render_twiki(self) -> str:
        """Render TWIKI report."""
        menu = MenuStub(self.eventSetup)
        menu.triggerGroups = self.getTriggerGroups(menu)
        data = dict(menu=menu)
        return TemplateEngine(self.searchpath).render("report.twiki", data)

    def write_html(self, filename: str) -> None:
        """Write HTML report to file, provided for convenience."""
        with open(filename, "wt") as handle:
            handle.write(self.render_html())

    def write_twiki(self, filename: str) -> None:
        """Write TWIKI report to file, provided for convenience."""
        with open(filename, "wt") as handle:
            handle.write(self.render_twiki())
