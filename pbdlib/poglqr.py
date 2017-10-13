import numpy as np
from utils.utils import lifted_transfer_matrix
import pbdlib as pbd

class PoGLQR(object):
	"""
	Implementation of LQR with Product of Gaussian as described in

		http://calinon.ch/papers/Calinon - HFR2016.pdf

	"""

	def __init__(self, A=None, B=None, nb_dim=2, dt=0.01, horizon=50):
		self._horizon = horizon
		self.A = A
		self.B = B
		self.nb_dim = nb_dim
		self.dt = dt

		self._s_xi, self._s_u = None, None
		self._x0 = None

		self._mvn_xi, self._mvn_u = None, None
		self._mvn_sol_xi, self._mvn_sol_u = None, None

		self._seq_xi, self._seq_u = None, None

	@property
	def u_dim(self):
		"""
		Number of dimension of input sequence lifted form
		:return:
		"""
		return self.nb_dim * self.horizon

	@property
	def xi_dim(self):

		"""
		Number of dimension of state sequence lifted form
		:return:
		"""
		return self.nb_dim * self.horizon * 2

	@property
	def mvn_sol_u(self):
		"""
		Distribution of control input after solving LQR
		:return:
		"""
		assert self.x0 is not None, "Please specify a starting state"
		assert self.mvn_xi is not None, "Please specify a target distribution"
		assert self.mvn_u is not None, "Please specify a control input distribution"

		if self._mvn_sol_u is None:
			self._mvn_sol_u =  self.mvn_xi.inv_trans_s(
				self.s_u, self.s_xi.dot(self.x0)) % self.mvn_u

		return self._mvn_sol_u

	@property
	def seq_xi(self):
		if self._seq_xi is None:
			self._seq_xi =  self.mvn_sol_xi.mu.reshape(self.horizon, self.nb_dim * 2)

		return self._seq_xi

	@property
	def seq_u(self):
		if self._seq_u is None:
			self._seq_u = self.mvn_sol_u.mu.reshape(self.horizon, self.nb_dim)

		return self._seq_u


	@property
	def mvn_sol_xi(self):
		"""
		Distribution of state after solving LQR
		:return:
		"""
		if self._mvn_sol_xi is None:
			self._mvn_sol_xi= self.mvn_sol_u.transform(
				self.s_u, self.s_xi.dot(self.x0))

		return self._mvn_sol_xi

	@property
	def mvn_xi(self):
		"""
		Distribution of state
		:return:
		"""
		return self._mvn_xi

	@mvn_xi.setter
	def mvn_xi(self, value):
		"""
		:param value 		[float] or [pbd.MVN]
		"""
		# resetting solution
		self._mvn_sol_xi = None
		self._mvn_sol_u = None
		self._seq_u = None
		self._seq_xi = None

		self._mvn_xi = value

	@property
	def mvn_u(self):
		"""
		Distribution of control input
		:return:
		"""
		return self._mvn_u

	@mvn_u.setter
	def mvn_u(self, value):
		"""
		:param value 		[float] or [pbd.MVN]
		"""
		# resetting solution
		self._mvn_sol_xi = None
		self._mvn_sol_u = None
		self._seq_u = None
		self._seq_xi = None

		if isinstance(value, pbd.MVN):
			self._mvn_u = value
		else:
			self._mvn_u = pbd.MVN(
				mu=np.zeros(self.u_dim), lmbda=10 ** value * np.eye(self.u_dim))

	@property
	def x0(self):
		return self._x0

	@x0.setter
	def x0(self, value):
		# resetting solution
		self._mvn_sol_xi = None
		self._mvn_sol_u = None

		self._x0 = value

	@property
	def s_u(self):
		if self._s_u is None:
			self._s_xi, self._s_u = lifted_transfer_matrix(self.A, self.B,
				horizon=self.horizon, dt=self.dt, nb_dim=self.nb_dim)
		return self._s_u

	@property
	def s_xi(self):
		if self._s_xi is None:
			self._s_xi, self._s_u = lifted_transfer_matrix(self.A, self.B,
				horizon=self.horizon, dt=self.dt, nb_dim=self.nb_dim)

		return self._s_xi

	@property
	def horizon(self):
		return self._horizon

	@horizon.setter
	def horizon(self, value):
		# reset everything
		self._s_xi, self._s_u = None, None
		self._x0 = None
		self._mvn_xi, self._mvn_u = None, None
		self._mvn_sol_xi, self._mvn_sol_u = None, None
		self._seq_xi, self._seq_u = None, None

		self._horizon = value