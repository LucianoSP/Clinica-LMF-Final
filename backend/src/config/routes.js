// Adicionar redirecionamento temporário (se necessário)
router.get('/api/pacientes/:id/dashboard', (req, res) => {
  res.redirect(301, `/api/pacientes/${req.params.id}`);
}); 