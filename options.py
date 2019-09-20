from conans import ConanFile



class OptionBase:
    """
    Base class for any Option class, that allow user to only implemente code that add option in argument lists.

    When package have a lot of options, code in ConanFile methods (configure, build, ...) become complex, hard
    to read and hard to maintain. Option class is here to help us.
    """
    def __init__( self, name, values, default_value, os_availability=None, requirements=None):
        self._name = name
        self._values = values
        self._default_value = default_value
        self._os_availability = os_availability
        self._requirements = requirements


    def collect_option( self, options ):
        """
        add this option in dictionary in destination of ConanFile.options attribute.
        """
        print( "{} = {}".format(self._name, self._values) )
        options[ self._name ] = self._values

    def collect_default_option( self, default_options ):
        """
        add this option in dictionary in destination of ConanFile.default_options attribute.
        """
        print( "{} = {}".format(self._name, self._default_value) )
        default_options[ self._name ] = self._default_value

    def config_options(self, conan):
        """
        call inside ConanFile.config_options() method. Remove this option if not available.
        """
        if not self._is_available(conan):
            delattr( conan.options, self._name )

    def requirements(self, conan):
        """
        call inside ConanFile.requirements() method. Add this option requirement if it is available and enable.
        """
        if self._is_available(conan) and self._requirements and self.is_enable(conan):
            conan.requires( self._requirements )

    def apply(self, conan, args):
        """
        Add this option in argument list to be used by build tool. Derived class should reimplement
        apply_if_available instead of this method.
        """
        if not self._is_available(conan):
            return
        self.apply_if_available( conan, args )

    def apply_if_available(self, conan, args):
        """
        Conveniant method to reimplement in base class to convert this option in build tool option.
        """
        pass



    def get_value(self, conan):
        """
        conveniant method to retrive this option's value in ConanFile.options attribute
        """
        return getattr( conan.options, self._name )

    def is_enable(self, conan):
        return self.get_value(conan) is True

    def _is_available(self, conan):
        return ( self._os_availability is None ) or ( str(conan.settings.os) in self._os_availability )




class GroupOption:
    """
    GroupOption encapsulate options.
    """
    def __init__( self, option, sub_options):
        self._option = option
        self._sub_options = sub_options

    def collect_option( self, options ):
        self.option.collect_option( options )
        for o in self._sub_options:
            o.collect_option( options )

    def collect_default_option( self, default_options ):
        self.option.collect_default_option( options )
        for o in self._sub_options:
            o.collect_default_option( default_options )

    def config_options( self, conan ):
        self.option.config_options( conan )
        for o in self._sub_options:
            o.config_options( conan )

    def requirements( self, conan ):
        if self._is_available(conan) and self.is_enable(conan):
            if self._requirements:
                super{}.config_options( conan )

            for o in self._sub_options:
                o.config_options( conan )
                conan.requires( self._requirements )

    def apply_if_available(self, conan, args):
        for o in self._sub_options:
            o.config_options( conan )
            conan.requires( self._requirements )


class SimpleOption(OptionBase):

    def __init__( self, name, default_values, option, os_availability=None, requirements=None):
        super().__init__(name, [True, False], default_values, os_availability, requirements)
        self._option = option

    def apply_option(self, conan, args):
        if self.get_value(conan):
            args.append( "-{}".format( self._option ) )

class PrependOption(OptionBase):

    def __init__( self, name, default_value, option, yes_prefix, no_prefix, os_availability=None, requirements=None):
        super().__init__(name, [True, False], default_value, os_availability, requirements)
        self._option  = option
        self._yes_prefix = yes_prefix
        self._no_prefix  = no_prefix

    def apply_option(self, conan, args):
        if self.get_value(conan):
            args.append( "-{}{}".format( self._yes_prefix, self._option ) )
        else:
            args.append( "-{}{}".format( self._no_prefix, self._option ) )


class NoOption(PrependOption):

    def __init__( self, name, default_value, option, os_availability=None, requirements=None):
        super().__init__(name, [True, False], default_value, option, "", "no-",  os_availability, requirements)


class YesNoOption(OptionBase):

    def __init__( self, name, default_value, option, os_availability=None, requirements=None):
        super().__init__(name, [True, False], default_value, os_availability, requirements)
        self._option = option

    def apply_option(self, conan, args):
        args.append("--{}=".format( self._option ) + ("yes" if conan.options[ self._name ] else "no"))

class SystemQtOption(OptionBase):

    def __init__( self, name, default_value, option, os_availability=None, requirements=None):
        super().__init__(name, [True, False], default_value, os_availability, requirements)
        self._option = option

    def apply_option(self, conan, args):
        args.append("--{}=".format( self._option ) + ("system" if conan.options[ self._name ] else "qt"))


class BinaryOption(OptionBase):

    def __init__( self, name, default_value, yes_option, no_option, os_availability=None, requirements=None):
        super().__init__(name, [True, False], default_value, os_availability, requirements)
        self._yes_option = yes_option
        self._no_option  = no_option

    def apply_option(self, conan, args):
        args.append("-{}".format( self._yes_option if getattr(conan.options, self._name ) else self._no_option ))


class ValueOption(OptionBase):

    def __init__( self, name, values, default_value, option, os_availability=None, requirements=None):
        super().__init__(name, values, default_value, os_availability, requirements)
        self._option  = option

    def apply_option(self, conan, args):
        args.append( "-{}={}".format( self._option, str( conan.options[ self._name ] ) ) )




def make_options_dict( options, options_objects ):
    for option in options_objects:
        option.collect_option( options )
    return options

def make_default_options_dict( default_options, options_objects ):
    for option in options_objects:
        option.collect_default_option( default_options )
    return default_options
