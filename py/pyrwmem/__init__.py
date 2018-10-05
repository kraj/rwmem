from .pyrwmem import *

class MappedRegister:
	def __init__(self, map, reg, size):
		self._map = map
		self._size = size
		self._reg = reg
		self._frozen = None
		self._initialized = True

	def __int__(self):
		return self.value

	def freeze(self):
		if not self._frozen is None:
			raise RuntimeError("Register already frozen")

		self._frozen = self._map.read(self._reg.offset, self._size)

	def unfreeze(self):
		return self._map.write(self._reg.offset, self._size, self._frozen)
		self._frozen = None

	def __getitem__(self, idx):
		if isinstance(idx, str):
			f = self._reg[idx]

			if not f:
				raise IndexError("Field not found")

			return get_field_value(self.value, f.high, f.low)

		elif isinstance(idx, int):
			if idx < 0 or idx >= self._size * 8:
				raise IndexError("Index out of bounds")

			return get_field_value(self.value, idx, idx)
		elif isinstance(idx, slice):
			indices = idx.indices(self._size * 8 - 1)

			low = indices[0]
			high = indices[1]

			if low > high:
				low, high = high, low

			return get_field_value(self.value, high, low)
		else:
			raise IndexError("Field not found")

	def __setitem__(self, idx, val):
		if isinstance(idx, str):
			f = self._reg[idx]

			if not f:
				raise IndexError("Field not found")

			v = self.value
			v = set_field_value(v, f.high, f.low, val)
			self.value = v

		elif isinstance(idx, int):
			if idx < 0 or idx >= self._size * 8:
				raise IndexError("Index out of bounds")

			v = self.value
			v = set_field_value(v, idx, idx, val)
			self.value = v

		elif isinstance(idx, slice):
			indices = idx.indices(self._size * 8 - 1)

			low = indices[0]
			high = indices[1]

			if low > high:
				low, high = high, low

			v = self.value
			v = set_field_value(v, high, low, val)
			self.value = v
		else:
			raise IndexError("Field not found")

	def __str__(self):
		return "{:#x}".format(self.value)

	def get_fields(self):
		self.freeze()

		fields = { }
		for f in self._reg:
			fields[f.name] = self[f.name]

		self.unfreeze()

		return fields

	def get_value(self):
		if self._frozen is None:
			return self._map.read(self._reg.offset, self._size)
		else:
			return self._frozen

	def set_value(self, val):
		if self._frozen is None:
			self._map.write(self._reg.offset, self._size, val)
		else:
			self._frozen = val

	def __contains__(self, v):
		return not self._reg[v] is None

	def __getattr__(self, name):
		if name in self:
			return self[name]
		elif name == "value":
			return self.get_value()
		elif name == "fields":
			return self.get_fields()
		else:
			raise AttributeError('No field {0} found!'.format(name))

	def __setattr__(self, name, value):
		if not self.__dict__.get('_initialized') or name in self.__dict__ or name in ["value", "fields"]:
			super().__setattr__(name, value)
			return

		if name in self:
			self[name] = value
		else:
			raise AttributeError('No field {0} found!'.format(name))

class MappedRegisterBlock:
	def __init__(self, file, regblock, offset = None):
		self._regblock = regblock

		self._map = MMapTarget(file, regblock.data_endianness, regblock.offset if offset is None else offset, self._regblock.size)

		self._initialized = True

	def __getitem__(self, idx):
		r = self._regblock[idx]

		if not r:
			raise IndexError("Register not found")

		return MappedRegister(self._map, r, self._regblock.data_size)

	def __setitem__(self, idx, val):
		if isinstance(idx, str):
			reg = self[idx]

			if isinstance(val, int):
				reg.value = val
			elif isinstance(val, dict):
				reg.freeze()
				for k,v in val.items():
					reg[k] = v
				reg.unfreeze()
			else:
				raise ValueError("Bad value")
		else:
			raise IndexError("Register not found")

	def __contains__(self, v):
		return not self._regblock[v] is None

	def __getattr__(self, name):
		if name in self:
			return self[name]
		else:
			raise AttributeError('No register {0} found!'.format(name))

	def __setattr__(self, name, value):
		if not self.__dict__.get('_initialized') or name in self.__dict__:
			super().__setattr__(name, value)
			return

		if name in self:
			self[name] = value
		else:
			raise AttributeError('No register {0} found!'.format(name))

