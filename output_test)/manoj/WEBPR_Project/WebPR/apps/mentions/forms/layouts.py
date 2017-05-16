from crispy_forms.layout import Field, Layout, HTML, Div

add_btn = HTML('<a href="#" class="btn btn-rounded sm btn-blue pull-right '
               'click-handler" data-handler="addField" '
               'onclick="return false;">+</a>')


class DivCol6(Div):
    """Class for wrapping inputs.

    Wrap with <div class="col-md-6 col-xs-6"></div>.

    """
    css_class = "col-md-6 col-xs-6"


class DivRow(Div):
    """Class for wrapping inputs.

    <div class="row"></div> tag.

    """
    css_class = "row"


merchant_layout = Layout(
    DivRow(
        DivCol6(
            Div(Field('official_name')),
            Div(add_btn, Field('short_name')),
            Div(Field('address', placeholder='Address')),
            Div(
                Div(Field('city', placeholder='City'),
                    css_class='col-md-5 pl0 pr0'),
                Div(Field('state', placeholder='ST'),
                    css_class='col-md-4 pr0 pl10'),
                Div(Field('zip_code', placeholder='ZIP'),
                    css_class='col-md-3 pl10 pr0')
            ),
            Div(
                Field('location')
            ),
            Div(Field('contact_info')),
        ),
        DivCol6(
            Div(add_btn, Field('phone', placeholder='XXX-XXX-XXXX'),
                css_class='phone-masked-input'),
            Div(add_btn, Field('product')),
            Div(add_btn, Field('web_page')),
            Div(add_btn, Field('ceo')),
            Div(Field('dda')),
            Div(Field('category', css_class='chosen-select'))
        )
    ),
    Div(Field('sources'), css_class='checkboxes-inline checkboxes-nomargin'),
    Div(Field('exclude_words')),
    Div(Field('search_settings'), css_class='hidden'),
    Div(
        HTML('<button type="submit" '
             '        class="btn btn-lg btn-blue w160 click-handler" '
             '        data-handler="create" '
             '        onclick="return false;">Submit</button>'),
        css_class="text-center mt25"
    )
)
