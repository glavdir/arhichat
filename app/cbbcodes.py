import bbcode

def get_parser():
    parser = bbcode.Parser()
    parser.add_formatter('post',    render_post)
    parser.add_formatter('thread',  render_thread)
    parser.add_formatter('dialog',  render_dialog)
    parser.add_formatter('arhibash',render_arhibash)
    parser.add_formatter('img',     render_img, replace_links = False)
    # parser.add_formatter('color',   render_color)

    return parser

def get_post_parser():
    parser = bbcode.Parser()
    parser.add_formatter('color', render_color)

    return parser

def render_post(name, value, options, parent, context):
    if 'post' in options:
        return "<a href = 'http://arhimag.org/showthread.php?p=%(postid)s#post%(value)s'>%(value)s</a>" % {'postid': options['post'], 'value': value}
    else:
        return value

def render_img(name, value, options, parent, context):
    return "<img class='img_true' src = '%(img)s'</img> <a class='img_false' href = '%(img)s'>%(img)s</a>" % {'img': value}

def render_thread(name, value, options, parent, context):
    if 'thread' in options:
        return "<a href = 'http://arhimag.org/showthread.php?t=%(threadid)s'>%(value)s</a>" % {'threadid': options['thread'], 'value': value}
    else:
        return value

def render_dialog(name, value, options, parent, context):
    if 'dialog' in options:
        return "<span class=msglink data-dialog_id='%(dialog_id)s'>#%(dialog_id)s</span> %(value)s" % {'dialog_id': options['dialog'], 'value': value}
    else:
        return value

def render_arhibash(name, value, options, parent, context):
    # [arhibash]выложил(а)Архибаш![ / arhibash]
    return "<span class='bashlink'>%s</span>" % (value)

def render_color(name, value, options, parent, context):
    # return '<div class="colorpost" style="color:%s;">%s</div>' % (options['color'], value)
    return '<font color="%s">%s</font>' % (options['color'], value)
