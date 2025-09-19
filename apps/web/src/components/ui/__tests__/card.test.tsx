import { render, screen, fireEvent } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import { Card, CardHeader, CardTitle, CardDescription, CardContent, StatCard, AgentCard } from '../card';

describe('Card Components', () => {
  describe('Card', () => {
    it('renders correctly', () => {
      render(
        <Card>
          <CardContent>Test content</CardContent>
        </Card>
      );
      expect(screen.getByText('Test content')).toBeInTheDocument();
    });

    it('applies variant classes', () => {
      const { container } = render(<Card variant="glass">Content</Card>);
      expect(container.firstChild).toHaveClass('glass');
    });

    it('applies hover effects', () => {
      const { container } = render(<Card hover="lift">Content</Card>);
      expect(container.firstChild).toHaveClass('hover:scale-[1.02]');
    });
  });

  describe('StatCard', () => {
    it('renders stat information', () => {
      render(
        <StatCard
          title="Active Agents"
          value={8}
          description="Currently running"
          trend={{ value: 24, isPositive: true }}
        />
      );

      expect(screen.getByText('Active Agents')).toBeInTheDocument();
      expect(screen.getByText('8')).toBeInTheDocument();
      expect(screen.getByText('Currently running')).toBeInTheDocument();
      expect(screen.getByText('+24%')).toBeInTheDocument();
    });

    it('renders negative trend correctly', () => {
      render(
        <StatCard
          title="Response Time"
          value="2.4h"
          trend={{ value: 12, isPositive: false }}
        />
      );

      expect(screen.getByText('12%')).toBeInTheDocument();
    });

    it('renders with icon', () => {
      const icon = <span data-testid="test-icon">📊</span>;
      render(
        <StatCard
          title="Test Stat"
          value={100}
          icon={icon}
        />
      );

      expect(screen.getByTestId('test-icon')).toBeInTheDocument();
    });
  });

  describe('AgentCard', () => {
    const mockAgent = {
      id: 1,
      name: 'Test Agent',
      description: 'A test agent',
      status: 'active',
      agent_type: 'code_reviewer',
      total_executions: 100,
      successful_executions: 95,
      last_execution_at: '2024-01-15T10:00:00Z',
    };

    it('renders agent information', () => {
      render(<AgentCard agent={mockAgent} />);

      expect(screen.getByText('Test Agent')).toBeInTheDocument();
      expect(screen.getByText('A test agent')).toBeInTheDocument();
      expect(screen.getByText('active')).toBeInTheDocument();
      expect(screen.getAllByText('95%')).toHaveLength(2); // Success rate appears twice
      expect(screen.getByText('100')).toBeInTheDocument(); // Total executions
    });

    it('calls onExecute when execute button is clicked', () => {
      const onExecute = vi.fn();
      render(<AgentCard agent={mockAgent} onExecute={onExecute} />);

      const executeButton = screen.getByText('Execute');
      fireEvent.click(executeButton);

      expect(onExecute).toHaveBeenCalledWith(1);
    });

    it('disables execute button for inactive agents', () => {
      const inactiveAgent = { ...mockAgent, status: 'inactive' };
      const onExecute = vi.fn();
      
      render(<AgentCard agent={inactiveAgent} onExecute={onExecute} />);

      const executeButton = screen.getByText('Execute');
      expect(executeButton).toBeDisabled();
    });
  });
});
