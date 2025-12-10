import { describe, it, expect } from 'vitest'
import { mount } from '@vue/test-utils'
import ChartCard from '../ChartCard.vue'

describe('ChartCard', () => {
  it('renders title correctly', () => {
    const wrapper = mount(ChartCard, {
      props: {
        title: 'Test Chart'
      }
    })

    expect(wrapper.text()).toContain('Test Chart')
  })

  it('renders icon when provided', () => {
    const wrapper = mount(ChartCard, {
      props: {
        title: 'Test Chart',
        icon: '📊'
      }
    })

    expect(wrapper.text()).toContain('📊')
  })

  it('emits expand event when expand button is clicked', async () => {
    const wrapper = mount(ChartCard, {
      props: {
        title: 'Test Chart'
      }
    })

    await wrapper.find('.expand-button').trigger('click')

    expect(wrapper.emitted('expand')).toBeTruthy()
    expect(wrapper.emitted('expand')).toHaveLength(1)
  })

  it('renders slot content', () => {
    const wrapper = mount(ChartCard, {
      props: {
        title: 'Test Chart'
      },
      slots: {
        default: '<div class="test-content">Chart Content</div>'
      }
    })

    expect(wrapper.find('.test-content').exists()).toBe(true)
    expect(wrapper.text()).toContain('Chart Content')
  })
})