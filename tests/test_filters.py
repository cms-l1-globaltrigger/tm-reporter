from tmReporter import filters


class TestFormatter:

    def test_snakecase(self):
        result = filters.snakecase("CamelCaseLabel")
        assert "camel_case_label" == result

    def test_vhdl_label(self):
        result = filters.vhdl_label("001FooBar.value__@2_")
        assert "d001_foo_bar_value_2" == result

    def test_vhdl_expression(self):
        result = filters.vhdl_expression("(singleMu_1 and doubleMu_2)")
        assert "( single_mu_1 and double_mu_2 )" == result

    def test_expr2html(self):
        result = filters.expr2html("comb{MU1,MU2}")
        assert '<span class="function">comb</span><span class="curl">{</span>MU1, MU2<span class="curl">}</span>' == result

    def test_vhdl2html(self):
        result = filters.vhdl2html("mu1 and jet2")
        assert '<span class="vhdlsig">mu1</span> <span class="vhdlop">and</span> <span class="vhdlsig">jet2</span>' == result
