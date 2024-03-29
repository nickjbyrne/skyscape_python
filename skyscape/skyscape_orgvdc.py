__author__ = 'prossi'
import skyscape


class lazy_property(object):
    def __init__(self, fget):
        self.fget = fget
        self.func_name = fget.__name__

    def __get__(self, obj, cls):
        if obj is None:
            return None
        value = self.fget(obj)
        setattr(obj, self.func_name, value)
        return value


class ORGVDC:
    def __init__(self, obj, connection):
        self.__dict__ = dict(obj.attrib)
        self.connection = connection
        self.rawxml = skyscape.etree.tostring(obj, pretty_print=True)

    @lazy_property
    def orgvdc_data(self):
        return skyscape.objectify.fromstring(self.connection.get_link(self.href))

    @lazy_property
    def links(self):
        holder = []
        for link in self.orgvdc_data.Link:
            new_method = skyscape.skyscape_vcloud_methods.Vcloud_Method(link, self.connection)
            if new_method.description != "":
                holder.append(new_method)
        return holder

    def list_links(self):
        i = 0
        for a in self.links:
            outputstring = "ID {0}: {1} - {2} - {3}".format(i, a.rel, a.description, a.href)
            i += 1
            print outputstring

    def compose_vapp(self, name, description):
        composevapplink = ""
        for link in self.links:
            if 'composeVApp' in link.href:
                composevapplink = link

        if composevapplink != "":
            composexml = """
            <ComposeVAppParams xmlns="http://www.vmware.com/vcloud/v1.5" xmlns:ovf="http://schemas.dmtf.org/ovf/envelope/1" name="{0}">
               <Description>{1}</Description>
               <AllEULAsAccepted>true</AllEULAsAccepted>
            </ComposeVAppParams>
            """.format(name, description)
            res = composevapplink.invoke(composexml)
            return res
        else:
            print "could not find composeVApp method on this VDC"
            return None
