// Main JavaScript for Restaurant Menu System

$(document).ready(function() {
    // Initialize tooltips
    $('[data-bs-toggle="tooltip"]').tooltip();
    
    // Initialize popovers
    $('[data-bs-toggle="popover"]').popover();
    
    // Auto-hide alerts after 5 seconds
    setTimeout(function() {
        $('.alert').fadeOut('slow');
    }, 5000);
    
    // Form validation
    $('form').on('submit', function(e) {
        var form = $(this);
        var isValid = true;
        
        // Check required fields
        form.find('[required]').each(function() {
            if ($(this).val() === '') {
                $(this).addClass('is-invalid');
                isValid = false;
            } else {
                $(this).removeClass('is-invalid');
            }
        });
        
        if (!isValid) {
            e.preventDefault();
            showAlert('danger', 'Lütfen tüm gerekli alanları doldurunuz.');
        }
    });
    
    // Phone number formatting
    $('input[name="phone"]').on('input', function() {
        var value = $(this).val().replace(/\D/g, '');
        if (value.length > 0) {
            if (value.length <= 3) {
                value = value;
            } else if (value.length <= 6) {
                value = value.slice(0, 3) + ' ' + value.slice(3);
            } else if (value.length <= 8) {
                value = value.slice(0, 3) + ' ' + value.slice(3, 6) + ' ' + value.slice(6);
            } else {
                value = value.slice(0, 3) + ' ' + value.slice(3, 6) + ' ' + value.slice(6, 8) + ' ' + value.slice(8, 10);
            }
        }
        $(this).val(value);
    });
    
    // Price formatting
    $('input[name="price"]').on('input', function() {
        var value = $(this).val().replace(/[^0-9.,]/g, '');
        $(this).val(value);
    });
    
    // Add to cart functionality
    $('.add-to-cart-form').on('submit', function(e) {
        e.preventDefault();
        
        var form = $(this);
        var productId = form.find('input[name="product_id"]').val();
        var quantityField = form.find('select[name="quantity"], input[name="quantity"]');
        var quantityValue = quantityField.length ? quantityField.val() : 1;
        var quantity = parseInt(quantityValue, 10);
        if (!quantity || isNaN(quantity)) {
            quantity = 1;
        }
        var button = form.find('button[type="submit"]');
        
        // Disable button and show loading
        button.prop('disabled', true);
        button.html('<i class="fas fa-spinner fa-spin me-1"></i>Ekleniyor...');
        
        $.ajax({
            url: '/user/add-to-cart',
            method: 'POST',
            data: {
                product_id: productId,
                quantity: quantity
            },
            success: function(response) {
                if (response.success) {
                    // Toast popup: ürün adıyla bilgi ver
                    try { showToast(response.product_name + ' Sepete Eklendi! ♥'); } catch (e) { showAlert('success', response.message); }
                    // Update cart count if exists
                    updateCartCount();
                } else {
                    showAlert('danger', response.message);
                }
            },
            error: function() {
                showAlert('danger', 'Bir hata oluştu! Lütfen tekrar deneyin.');
            },
            complete: function() {
                // Re-enable button
                button.prop('disabled', false);
                button.html('<i class="fas fa-plus me-1"></i>Sepete Ekle');
            }
        });
    });
    
    // Update cart quantity
    $('.update-quantity-form').on('submit', function(e) {
        e.preventDefault();
        
        var form = $(this);
        var itemId = form.find('input[name="item_id"]').val();
        var quantity = form.find('input[name="quantity"]').val();
        
        $.ajax({
            url: '/user/update-cart',
            method: 'POST',
            data: {
                item_id: itemId,
                quantity: quantity
            },
            success: function(response) {
                if (response.success) {
                    location.reload();
                } else {
                    showAlert('danger', response.message);
                }
            },
            error: function() {
                showAlert('danger', 'Bir hata oluştu!');
            }
        });
    });
    
    // Search functionality
    $('#searchInput').on('keyup', function() {
        var searchTerm = $(this).val().toLowerCase();
        $('.product-card').each(function() {
            var productName = $(this).data('name') || $(this).find('.card-title').text().toLowerCase();
            if (productName.includes(searchTerm)) {
                $(this).show();
            } else {
                $(this).hide();
            }
        });
    });
    
    // Order status update
    $('.update-order-status').on('click', function() {
        var orderId = $(this).data('order-id');
        var newStatus = $(this).data('status');
        
        if (confirm('Sipariş durumunu güncellemek istediğinizden emin misiniz?')) {
            $.ajax({
                url: '/api/order/' + orderId + '/status',
                method: 'POST',
                data: { status: newStatus },
                success: function(response) {
                    if (response.success) {
                        location.reload();
                    } else {
                        showAlert('danger', response.message);
                    }
                },
                error: function() {
                    showAlert('danger', 'Bir hata oluştu!');
                }
            });
        }
    });
    
    // Table status update
    $('.update-table-status').on('click', function() {
        var tableId = $(this).data('table-id');
        var newStatus = $(this).data('status');
        
        $.ajax({
            url: '/api/table/' + tableId + '/status',
            method: 'POST',
            data: { status: newStatus },
            success: function(response) {
                if (response.success) {
                    location.reload();
                } else {
                    showAlert('danger', response.message);
                }
            },
            error: function() {
                showAlert('danger', 'Bir hata oluştu!');
            }
        });
    });
    
    // Print functionality
    $('.print-btn').on('click', function() {
        window.print();
    });
    
    // Export functionality
    $('.export-btn').on('click', function() {
        var format = $(this).data('format');
        var tableId = $(this).data('table-id');
        
        if (format === 'pdf') {
            window.open('/api/export/table/' + tableId + '/pdf', '_blank');
        } else if (format === 'excel') {
            window.open('/api/export/table/' + tableId + '/excel', '_blank');
        }
    });
});

// Utility functions
function showAlert(type, message) {
    var alertHtml = '<div class="alert alert-' + type + ' alert-dismissible fade show" role="alert">' +
                   message +
                   '<button type="button" class="btn-close" data-bs-dismiss="alert"></button>' +
                   '</div>';
    $('main .container').prepend(alertHtml);
    
    setTimeout(function() {
        $('.alert').fadeOut();
    }, 5000);
}

// Simple bootstrap-like toast
function showToast(message) {
    var wrapper = $('<div class="position-fixed top-0 end-0 p-3" style="z-index: 1080;"></div>');
    var toastHtml = $('<div class="toast align-items-center text-bg-success border-0 show" role="alert" aria-live="assertive" aria-atomic="true">\
      <div class="d-flex">\
        <div class="toast-body">' + message + '</div>\
        <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast" aria-label="Close"></button>\
      </div>\
    </div>');
    wrapper.append(toastHtml);
    $('body').append(wrapper);
    setTimeout(function() { wrapper.fadeOut(300, function(){ $(this).remove(); }); }, 2500);
}

function updateCartCount() {
    $.ajax({
        url: '/api/cart/count',
        method: 'GET',
        success: function(response) {
            $('.cart-count').text(response.count);
        }
    });
}

function updateOrderDisplay(order) {
    var orderRow = $('tr[data-order-id="' + order.id + '"]');
    if (orderRow.length) {
        orderRow.find('.order-status').text(order.status);
        orderRow.find('.order-total').text(order.total_amount + ' ₺');
    }
}

function updateTableDisplay(table) {
    var tableCard = $('.table-card[data-table-id="' + table.id + '"]');
    if (tableCard.length) {
        tableCard.find('.table-status').text(table.is_occupied ? 'Dolu' : 'Boş');
        tableCard.find('.table-total').text(table.total_amount + ' ₺');
    }
}

function formatCurrency(amount) {
    return new Intl.NumberFormat('tr-TR', {
        style: 'currency',
        currency: 'TRY'
    }).format(amount);
}

function formatDate(dateString) {
    return new Date(dateString).toLocaleDateString('tr-TR', {
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });
}

// Confirmation dialogs
function confirmDelete(message) {
    return confirm(message || 'Bu işlemi gerçekleştirmek istediğinizden emin misiniz?');
}

function confirmOrder(message) {
    return confirm(message || 'Siparişinizi onaylıyor musunuz?');
}

function confirmPayment(message) {
    return confirm(message || 'Ödemeyi tamamlamak istediğinizden emin misiniz?');
}

// Loading states
function showLoading(element) {
    $(element).prop('disabled', true);
    $(element).html('<i class="fas fa-spinner fa-spin me-1"></i>Yükleniyor...');
}

function hideLoading(element, originalText) {
    $(element).prop('disabled', false);
    $(element).html(originalText);
}

// Form validation helpers
function validateEmail(email) {
    var re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return re.test(email);
}

function validatePhone(phone) {
    var re = /^[\d\s\+\-\(\)]+$/;
    return re.test(phone) && phone.replace(/\D/g, '').length >= 10;
}

function validatePrice(price) {
    var re = /^\d+(\.\d{1,2})?$/;
    return re.test(price);
}
