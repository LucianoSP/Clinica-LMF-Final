import React, { useState } from 'react';
import { 
  Button,
  Card, 
  Divider,
  Form, 
  Input,
  InputNumber,
  Alert,
  Spin,
  Progress,
  Space,
  Typography
} from 'antd';
import axios from 'axios';

const { Title, Text } = Typography;

const ImportarAgendamentos = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [resultado, setResultado] = useState(null);
  const [erro, setErro] = useState(null);
  
  const handleSubmit = async (values) => {
    setLoading(true);
    setResultado(null);
    setErro(null);
    
    try {
      const response = await axios.post('/api/agendamentos/importar', values);
      const data = response.data;
      
      if (data.success) {
        setResultado(data);
      } else {
        setErro(data.message || 'Erro na importação');
      }
    } catch (error) {
      setErro(`Erro ao executar importação: ${error.message}`);
      console.error('Erro completo:', error);
    } finally {
      setLoading(false);
    }
  };
  
  return (
    <div className="importacao-container" style={{ maxWidth: '800px', margin: '0 auto', padding: '20px' }}>
      <Card
        title={<Title level={3}>Importar Agendamentos do MySQL</Title>}
        bordered={true}
      >
        <Form form={form} onFinish={handleSubmit} layout="vertical">
          <Form.Item 
            name="database" 
            label="Database" 
            rules={[{ required: true, message: 'Informe o nome do banco de dados' }]}
          >
            <Input placeholder="Nome do banco de dados MySQL" />
          </Form.Item>
          
          <Form.Item 
            name="tabela" 
            label="Tabela" 
            initialValue="ps_schedule"
          >
            <Input placeholder="Nome da tabela (padrão: ps_schedule)" />
          </Form.Item>
          
          <Form.Item 
            name="limit" 
            label="Limite de Registros" 
          >
            <InputNumber min={1} placeholder="Opcional: limite de registros" style={{ width: '100%' }} />
          </Form.Item>
          
          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} block>
              Iniciar Importação
            </Button>
          </Form.Item>
        </Form>
        
        {loading && (
          <div style={{ marginTop: 20, textAlign: 'center' }}>
            <Spin size="large" tip="Processando importação..." />
          </div>
        )}
        
        {erro && (
          <Alert 
            message="Erro na Importação" 
            description={erro} 
            type="error" 
            showIcon 
            style={{ marginTop: 20 }}
          />
        )}
        
        {resultado && (
          <div style={{ marginTop: 20 }}>
            <Alert 
              message="Importação Concluída" 
              description={resultado.message} 
              type="success" 
              showIcon 
            />
            
            <Card style={{ marginTop: 16 }} size="small" title="Estatísticas">
              <Progress 
                percent={Math.round((resultado.importados) / Math.max(resultado.total, 1) * 100)} 
                success={{ percent: Math.round((resultado.importados - resultado.total_atualizados) / Math.max(resultado.total, 1) * 100) }}
                format={() => `${resultado.importados}/${resultado.total}`}
              />
              <Space direction="vertical" style={{ width: '100%', marginTop: 10 }}>
                <Text>Total de agendamentos processados: {resultado.total}</Text>
                <Text>Novos agendamentos: {resultado.importados - resultado.total_atualizados}</Text>
                <Text>Agendamentos atualizados: {resultado.total_atualizados}</Text>
                <Text>Erros: {resultado.total_erros}</Text>
              </Space>
            </Card>
            
            {resultado.erros && resultado.erros.length > 0 && (
              <Card style={{ marginTop: 16 }} size="small" title="Erros">
                {resultado.erros.map((erro, index) => (
                  <p key={index}>
                    <Text strong>Agendamento {erro.agendamento}:</Text> {erro.erro}
                  </p>
                ))}
              </Card>
            )}
          </div>
        )}
      </Card>
    </div>
  );
};

export default ImportarAgendamentos; 